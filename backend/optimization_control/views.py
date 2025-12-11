from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from data_acquisition.models import Device, DeviceReading
from simulation.models import GenerationHistory, BatteryState


OFFPEAK_HOURS = {22, 23, 0, 1, 2, 3, 4, 5}


def _parse_dt(value: str, tz):
    return timezone.datetime.fromisoformat(value).replace(tzinfo=tz)


def _device_power_kw(device: Device, end_dt):
    reading = (
        DeviceReading.objects.filter(device=device, timestamp__lte=end_dt)
        .order_by("-timestamp")
        .first()
    )
    power_kw = 1.0
    priority = 5
    if reading:
        power_kw = reading.value if reading.metric.lower() == "power_kw" else 1.0
        priority = reading.priority
    return power_kw, priority


class OptimizationRecommendation(APIView):
    """
    Generuje rekomendację harmonogramu włączania urządzeń:
    - uruchamia najpierw urządzenia wysokiego priorytetu,
    - urządzenia niskiego priorytetu pakuje w tańsze godziny (off-peak 22-6),
    - bateria używana na początku aż do wyczerpania.
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

        # slots
        slots = []
        cur = start_dt
        while cur < end_dt:
            slots.append(cur)
            cur += timedelta(hours=1)

        offpeak_slots = [s for s in slots if s.hour in OFFPEAK_HOURS]
        peak_slots = [s for s in slots if s.hour not in OFFPEAK_HOURS]

        # generation reference
        gen_qs = GenerationHistory.objects.filter(timestamp__gte=start_dt, timestamp__lt=end_dt)
        total_generation_kw = float(sum(g.total_generation_kw for g in gen_qs)) if gen_qs.exists() else 0.0

        # battery
        battery, _ = BatteryState.objects.get_or_create(id=1, defaults={"max_capacity_kwh": Decimal("100.000")})
        battery_available = float(battery.current_charge_kwh)

        # build schedule
        schedule = []
        battery_remaining = battery_available
        off_idx = 0
        peak_idx = 0

        # sort devices: higher priority number = lower priority -> schedule low priority in offpeak
        devices_with_meta = []
        for d in devices:
            power_kw, prio = _device_power_kw(d, end_dt)
            devices_with_meta.append((d, power_kw, prio))
        devices_with_meta.sort(key=lambda x: x[2])  # ascending priority

        for device, power_kw, prio in devices_with_meta:
            duration_h = 1
            need_kwh = power_kw * duration_h

            # choose slot: low priority (prio high number) -> offpeak if available
            if prio >= 3 and off_idx < len(offpeak_slots):
                start_slot = offpeak_slots[off_idx]
                off_idx += 1
                tariff = "offpeak"
            else:
                if peak_idx < len(peak_slots):
                    start_slot = peak_slots[peak_idx]
                    peak_idx += 1
                elif off_idx < len(offpeak_slots):
                    start_slot = offpeak_slots[off_idx]
                    off_idx += 1
                else:
                    start_slot = slots[-1]
                tariff = "peak"

            battery_used = min(battery_remaining, need_kwh)
            battery_remaining -= battery_used
            source = "battery+grid" if battery_used > 0 else f"{tariff}_grid"

            schedule.append(
                {
                    "device_id": device.device_id,
                    "device_name": device.name,
                    "priority": prio,
                    "power_kw": power_kw,
                    "start": start_slot.isoformat(),
                    "end": (start_slot + timedelta(hours=duration_h)).isoformat(),
                    "tariff": tariff,
                    "energy_kwh": need_kwh,
                    "battery_used_kwh": round(battery_used, 3),
                    "source": source,
                }
            )

        total_demand = sum(item["energy_kwh"] for item in schedule)
        battery_used_total = battery_available - battery_remaining

        return Response(
            {
                "window": {"start": start_dt.isoformat(), "end": end_dt.isoformat()},
                "summary": {
                    "devices": len(schedule),
                    "total_demand_kwh": round(total_demand, 3),
                    "generation_kw_window_sum": round(total_generation_kw, 3),
                    "battery_start_kwh": round(battery_available, 3),
                    "battery_used_kwh": round(battery_used_total, 3),
                    "battery_remaining_kwh": round(battery_remaining, 3),
                },
                "schedule": schedule,
                "assumptions": {
                    "offpeak_hours": sorted(list(OFFPEAK_HOURS)),
                    "duration_h_default": 1,
                    "priority_rule": "priorytet >=3 -> offpeak jeśli dostępne; mniejszy -> ASAP",
                    "power_kw_source": "metric=='power_kw' z DeviceReading lub 1.0 gdy brak",
                },
            }
        )