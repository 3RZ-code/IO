from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SimDevice, GenerationHistory, BatteryState
from .serializers import GenerationHistorySerializer, SimDeviceSerializer, BatteryStateSerializer
from .services import (
    simulate_generation_from_weather,
    estimate_energy_kwh_for_forecast,
    ensure_randomized_today,
    adjust_battery,
    generate_mock_weather,
    generate_mock_series,
)
from .serializers import BatteryLogSerializer
from .models import BatteryLog


class SimDeviceList(generics.ListAPIView):
    queryset = SimDevice.objects.all().order_by("device_id")
    serializer_class = SimDeviceSerializer


class GenerationHistoryListCreate(generics.ListCreateAPIView):
    queryset = GenerationHistory.objects.all()
    serializer_class = GenerationHistorySerializer


class GenerationHistoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GenerationHistory.objects.all()
    serializer_class = GenerationHistorySerializer


class RunGenerationSimulation(APIView):
    """
    Generuje symulację na bazie losowej pogody (bez zewnętrznego API) i zapisuje do historii.
    """

    def post(self, request):
        weather = generate_mock_weather()
        try:
            history_entry = simulate_generation_from_weather(weather)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GenerationHistorySerializer(history_entry)
        return Response(
            {
                "history": serializer.data,
                "summary": {
                    "pv_generation_kw": history_entry.pv_generation_kw,
                    "wind_generation_kw": history_entry.wind_generation_kw,
                    "total_generation_kw": history_entry.total_generation_kw,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class RunGenerationSimulationRange(APIView):
    """
    Generuje i zapisuje symulacje od dnia start do end (YYYY-MM-DD), korzystając z mockowanej pogody.
    Opcjonalnie step_hours (domyślnie 3).
    """

    def post(self, request):
        start = request.data.get("start")
        end = request.data.get("end")
        step_hours = request.data.get("step_hours", 3)

        if not start or not end:
            return Response({"detail": "Podaj start i end w formacie YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            step_hours = int(step_hours)
            if step_hours <= 0:
                raise ValueError()
        except Exception:
            return Response({"detail": "step_hours musi być dodatnią liczbą całkowitą."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tz = timezone.get_current_timezone()
            start_dt = timezone.datetime.fromisoformat(start).replace(tzinfo=tz)
            end_dt = timezone.datetime.fromisoformat(end).replace(tzinfo=tz)
        except Exception:
            return Response({"detail": "Nieprawidłowy format daty (oczekiwany YYYY-MM-DD)."}, status=status.HTTP_400_BAD_REQUEST)

        if end_dt < start_dt:
            return Response({"detail": "end musi być >= start."}, status=status.HTTP_400_BAD_REQUEST)

        # ustaw koniec na 23:59:59 danego dnia
        end_dt = end_dt + timezone.timedelta(days=1) - timezone.timedelta(seconds=1)

        series = generate_mock_series(start_dt, end_dt, step_hours=step_hours)
        entries = []
        for weather in series:
            entry = simulate_generation_from_weather(weather)
            entries.append(entry)

        serializer = GenerationHistorySerializer(entries, many=True)
        return Response(
            {
                "count": len(entries),
                "start": start_dt.date().isoformat(),
                "end": (end_dt.date()).isoformat(),
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class TodayForecastEnergy(APIView):
    """
    Prognoza energii (kWh) na dziś na podstawie lokalnie generowanej serii (3h kroki).
    """

    def get(self, request):
        today = timezone.now().date()
        tz = timezone.get_current_timezone()
        start_dt = timezone.datetime.combine(today, timezone.datetime.min.time(), tzinfo=tz)
        end_dt = start_dt + timezone.timedelta(days=1) - timezone.timedelta(seconds=1)

        series = generate_mock_series(start_dt, end_dt, step_hours=3)
        energy = estimate_energy_kwh_for_forecast(series)
        return Response({"date": today.isoformat(), "energy_kwh": energy})


class LastMonthEnergy(APIView):
    """
    Energia (kWh) za ostatnie 30 dni na podstawie zapisanych symulacji GenerationHistory.
    Działa na darmowym planie OpenWeather (bo korzysta z lokalnie zapisanych wyników).
    """

    def get(self, request):
        today = timezone.now().date()
        start_date = today - timezone.timedelta(days=30)

        qs = (
            GenerationHistory.objects.filter(timestamp__date__gte=start_date, timestamp__date__lt=today)
            .annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(
                pv_energy_kwh=Sum("pv_generation_kw"),
                wind_energy_kwh=Sum("wind_generation_kw"),
                total_energy_kwh=Sum("total_generation_kw"),
            )
            .order_by("-day")
        )

        if not qs:
            return Response(
                {"detail": "Brak zapisanych symulacji dla ostatnich 30 dni. Uruchom /simulation/generation/run/."},
                status=status.HTTP_404_NOT_FOUND,
            )

        daily = [
            {
                "date": row["day"].isoformat(),
                "pv_energy_kwh": row["pv_energy_kwh"],
                "wind_energy_kwh": row["wind_energy_kwh"],
                "total_energy_kwh": row["total_energy_kwh"],
            }
            for row in qs
        ]

        total_pv = sum((row["pv_energy_kwh"] or 0) for row in qs)
        total_wind = sum((row["wind_energy_kwh"] or 0) for row in qs)
        total = sum((row["total_energy_kwh"] or 0) for row in qs)

        return Response(
            {
                "days": daily,
                "summary": {
                    "pv_energy_kwh": total_pv,
                    "wind_energy_kwh": total_wind,
                    "total_energy_kwh": total,
                },
            }
        )


class BatteryView(APIView):
    """
    GET  -> zwraca stan baterii i max pojemność (po wcześniejszym losowaniu o 00:00).
    POST -> body: {"action": "add"|"remove", "amount_kwh": <number>} i zwraca stan po operacji.
    """

    def get(self, request):
        battery = ensure_randomized_today()
        data = BatteryStateSerializer(battery).data
        return Response(data)


class MockWeatherRange(APIView):
    """
    Zwraca sztuczne dane pogody dla zakresu dat (inclusive) w krokach dobowych
    z dryfem +/-10% względem poprzedniej wartości.
    GET params: start=YYYY-MM-DD, end=YYYY-MM-DD
    """

    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if not start or not end:
            return Response({"detail": "Podaj parametry start i end w formacie YYYY-MM-DD."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            tz = timezone.get_current_timezone()
            start_dt = timezone.datetime.fromisoformat(start).replace(tzinfo=tz)
            end_dt = timezone.datetime.fromisoformat(end).replace(tzinfo=tz)
        except Exception:
            return Response({"detail": "Nieprawidłowy format daty (oczekiwany YYYY-MM-DD)."},
                            status=status.HTTP_400_BAD_REQUEST)

        if end_dt < start_dt:
            return Response({"detail": "end musi być >= start."}, status=status.HTTP_400_BAD_REQUEST)

        series = generate_mock_series(start_dt, end_dt, step_hours=24)
        return Response({"from": start_dt.date().isoformat(), "to": end_dt.date().isoformat(), "data": series})

    def post(self, request):
        action = request.data.get("action")
        amount = request.data.get("amount_kwh")
        if action not in ("add", "remove"):
            return Response({"detail": "action must be 'add' or 'remove'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount_dec = Decimal(str(amount))
        except Exception:
            return Response({"detail": "amount_kwh must be a number."}, status=status.HTTP_400_BAD_REQUEST)
        if amount_dec < 0:
            return Response({"detail": "amount_kwh must be non-negative."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            battery = adjust_battery(action, amount_dec)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        data = BatteryStateSerializer(battery).data
        return Response(data)


class BatteryHistoryView(generics.ListAPIView):
    queryset = BatteryLog.objects.all()
    serializer_class = BatteryLogSerializer
    pagination_class = None
