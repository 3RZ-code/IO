from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from data_acquisition.models import Device, DeviceReading
from simulation.models import GenerationHistory, BatteryState


# Ceny taryf (zł/kWh)
TARIFF_DAY_PRICE = 0.6212  # Strefa dzienna
TARIFF_NIGHT_PRICE = 0.6036  # Strefa nocna

# Harmonogram taryf
# Pon-Pt: 22-06 nocna, 13-15 nocna, reszta dzienna
# Weekend: cały dzień nocna
NIGHT_HOURS_WEEKDAY = {22, 23, 0, 1, 2, 3, 4, 5, 13, 14}  # 22-06 i 13-15


def _parse_dt(value: str, tz):
    return timezone.datetime.fromisoformat(value).replace(tzinfo=tz)


def _device_power_kw(device: Device, end_dt):
    reading = (
        DeviceReading.objects.filter(device=device, timestamp__lte=end_dt)
        .order_by("-timestamp")
        .first()
    )
    power_kw = 1.0
    if reading:
        power_kw = reading.value if reading.metric.lower() == "power_kw" else 1.0
    # Priority pobieramy z Device, nie z DeviceReading
    priority = device.priority if device.priority is not None else 5
    return power_kw, priority


def _get_tariff_for_datetime(dt):
    """
    Zwraca taryfę dla danego datetime.
    Returns: 'night' lub 'day'
    """
    weekday = dt.weekday()  # 0=Monday, 6=Sunday
    hour = dt.hour
    
    # Weekend (sobota=5, niedziela=6) - cały dzień nocna
    if weekday >= 5:
        return 'night'
    
    # Pon-Pt
    if hour in NIGHT_HOURS_WEEKDAY:
        return 'night'
    else:
        return 'day'


def _get_tariff_price(tariff):
    """Zwraca cenę taryfy w zł/kWh"""
    return TARIFF_NIGHT_PRICE if tariff == 'night' else TARIFF_DAY_PRICE


def _calculate_cost(energy_kwh, tariff):
    """Oblicza koszt energii w zł"""
    price = _get_tariff_price(tariff)
    return round(energy_kwh * price, 4)


class OptimizationRecommendation(APIView):
    """
    Generuje rekomendację harmonogramu włączania urządzeń z uwzględnieniem taryf:
    - Taryfa dzienna: 0.6212 zł/kWh
    - Taryfa nocna: 0.6036 zł/kWh
    - Pon-Pt: 22-06 i 13-15 nocna, reszta dzienna
    - Weekend: cały dzień nocna
    - Oblicza oszczędności przy optymalizacji harmonogramu
    - Używa danych z data_acquisition i simulation
    """

    def post(self, request):
        tz = timezone.get_current_timezone()

        start_raw = request.data.get("start")
        end_raw = request.data.get("end")
        if start_raw and end_raw:
            try:
                start_dt = _parse_dt(start_raw, tz)
                end_dt = _parse_dt(end_raw, tz)
            except Exception:
                return Response({"detail": "start/end w formacie YYYY-MM-DDTHH:MM:SS"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            start_dt = timezone.now()
            end_dt = start_dt + timedelta(hours=24)

        if end_dt <= start_dt:
            return Response({"detail": "end musi być > start"}, status=status.HTTP_400_BAD_REQUEST)

        devices = Device.objects.filter(is_active=True).order_by("device_id")
        if not devices.exists():
            return Response({"detail": "Brak aktywnych urządzeń w data_acquisition.Device"}, status=status.HTTP_404_NOT_FOUND)

        # Generuj sloty czasowe (co godzinę)
        slots = []
        cur = start_dt
        while cur < end_dt:
            slots.append(cur)
            cur += timedelta(hours=1)

        # Podziel sloty na taryfy
        night_slots = [s for s in slots if _get_tariff_for_datetime(s) == 'night']
        day_slots = [s for s in slots if _get_tariff_for_datetime(s) == 'day']

        # Produkcja energii z simulation
        gen_qs = GenerationHistory.objects.filter(timestamp__gte=start_dt, timestamp__lt=end_dt)
        total_generation_kwh = float(sum(g.total_generation_kw for g in gen_qs)) if gen_qs.exists() else 0.0

        # Bateria z simulation
        battery, _ = BatteryState.objects.get_or_create(id=1, defaults={"max_capacity_kwh": Decimal("100.000")})
        battery_available = float(battery.current_charge_kwh)

        # Pobierz dane urządzeń
        devices_with_meta = []
        for d in devices:
            power_kw, prio = _device_power_kw(d, end_dt)
            devices_with_meta.append((d, power_kw, prio))
        
        # Sortuj po priorytecie (niższy priorytet = wyższa liczba = później)
        devices_with_meta.sort(key=lambda x: x[2])  # ascending priority

        # OPTYMALNY harmonogram (niskie priorytety -> taryfa nocna)
        optimal_schedule = []
        battery_remaining_optimal = battery_available
        night_idx = 0
        day_idx = 0

        for device, power_kw, prio in devices_with_meta:
            duration_h = 1
            need_kwh = power_kw * duration_h

            # Wybierz slot: niski priorytet (>=2) -> taryfa nocna jeśli dostępna
            if prio >= 2 and night_idx < len(night_slots):
                start_slot = night_slots[night_idx]
                night_idx += 1
                tariff = "night"
            else:
                if day_idx < len(day_slots):
                    start_slot = day_slots[day_idx]
                    day_idx += 1
                elif night_idx < len(night_slots):
                    start_slot = night_slots[night_idx]
                    night_idx += 1
                else:
                    start_slot = slots[-1]
                tariff = "day"

            battery_used = min(battery_remaining_optimal, need_kwh)
            battery_remaining_optimal -= battery_used
            grid_energy = need_kwh - battery_used
            cost = _calculate_cost(grid_energy, tariff)

            optimal_schedule.append({
                "device_id": device.device_id,
                "device_name": device.name,
                "priority": prio,
                "power_kw": power_kw,
                "start": start_slot.isoformat(),
                "end": (start_slot + timedelta(hours=duration_h)).isoformat(),
                "tariff": tariff,
                "energy_kwh": round(need_kwh, 3),
                "battery_used_kwh": round(battery_used, 3),
                "grid_energy_kwh": round(grid_energy, 3),
                "cost_pln": cost,
            })

        # REFERENCYJNY harmonogram (wszystko ASAP, bez optymalizacji)
        reference_schedule = []
        battery_remaining_ref = battery_available
        slot_idx = 0

        for device, power_kw, prio in devices_with_meta:
            duration_h = 1
            need_kwh = power_kw * duration_h

            if slot_idx < len(slots):
                start_slot = slots[slot_idx]
                slot_idx += 1
            else:
                start_slot = slots[-1]

            tariff = _get_tariff_for_datetime(start_slot)
            battery_used = min(battery_remaining_ref, need_kwh)
            battery_remaining_ref -= battery_used
            grid_energy = need_kwh - battery_used
            cost = _calculate_cost(grid_energy, tariff)

            reference_schedule.append({
                "device_id": device.device_id,
                "device_name": device.name,
                "priority": prio,
                "power_kw": power_kw,
                "start": start_slot.isoformat(),
                "end": (start_slot + timedelta(hours=duration_h)).isoformat(),
                "tariff": tariff,
                "energy_kwh": round(need_kwh, 3),
                "battery_used_kwh": round(battery_used, 3),
                "grid_energy_kwh": round(grid_energy, 3),
                "cost_pln": cost,
            })

        # Oblicz koszty i oszczędności
        optimal_total_cost = sum(item["cost_pln"] for item in optimal_schedule)
        reference_total_cost = sum(item["cost_pln"] for item in reference_schedule)
        savings_pln = round(reference_total_cost - optimal_total_cost, 4)
        savings_percent = round((savings_pln / reference_total_cost * 100) if reference_total_cost > 0 else 0, 2)

        # Oblicz różnicę w użyciu taryf
        optimal_night_kwh = sum(item["grid_energy_kwh"] for item in optimal_schedule if item["tariff"] == "night")
        optimal_day_kwh = sum(item["grid_energy_kwh"] for item in optimal_schedule if item["tariff"] == "day")
        reference_night_kwh = sum(item["grid_energy_kwh"] for item in reference_schedule if item["tariff"] == "night")
        reference_day_kwh = sum(item["grid_energy_kwh"] for item in reference_schedule if item["tariff"] == "day")

        total_demand = sum(item["energy_kwh"] for item in optimal_schedule)
        battery_used_total = battery_available - battery_remaining_optimal

        return Response({
            "window": {"start": start_dt.isoformat(), "end": end_dt.isoformat()},
            "tariffs": {
                "day_price_pln_per_kwh": TARIFF_DAY_PRICE,
                "night_price_pln_per_kwh": TARIFF_NIGHT_PRICE,
                "schedule": {
                    "weekday": "22:00-06:00 i 13:00-15:00 = nocna, reszta = dzienna",
                    "weekend": "cały dzień = nocna"
                }
            },
            "summary": {
                "devices_count": len(optimal_schedule),
                "total_demand_kwh": round(total_demand, 3),
                "generation_kwh": round(total_generation_kwh, 3),
                "battery_start_kwh": round(battery_available, 3),
                "battery_used_kwh": round(battery_used_total, 3),
                "battery_remaining_kwh": round(battery_remaining_optimal, 3),
            },
            "costs": {
                "optimal_total_pln": round(optimal_total_cost, 4),
                "reference_total_pln": round(reference_total_cost, 4),
                "savings_pln": savings_pln,
                "savings_percent": savings_percent,
            },
            "energy_distribution": {
                "optimal": {
                    "night_kwh": round(optimal_night_kwh, 3),
                    "day_kwh": round(optimal_day_kwh, 3),
                },
                "reference": {
                    "night_kwh": round(reference_night_kwh, 3),
                    "day_kwh": round(reference_day_kwh, 3),
                },
                "shift_to_night_kwh": round(optimal_night_kwh - reference_night_kwh, 3),
            },
            "optimal_schedule": optimal_schedule,
            "reference_schedule": reference_schedule,
        })