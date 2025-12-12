from datetime import datetime, timedelta, timezone as dt_timezone, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Iterable, List
import random
import json
from urllib import request

from django.utils import timezone

from .models import SimDevice, GenerationHistory, BatteryState, BatteryLog


LODZ_COORDS = {"lat": 51.7687323, "lon": 19.4569911, "label": "Lodz"}


class WeatherConnection:
    """
    Klasa do pobierania danych pogodowych z Open-Meteo API.
    """
    
    def __init__(self, latitude: float = None, longitude: float = None):
        self.latitude = latitude or LODZ_COORDS["lat"]
        self.longitude = longitude or LODZ_COORDS["lon"]
        self.stats = {}
    
    def connect(self):
        """Pobiera dane pogodowe z Open-Meteo API."""
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={self.latitude}&longitude={self.longitude}&"
            f"daily=wind_speed_10m_max,shortwave_radiation_sum,temperature_2m_max,"
            f"temperature_2m_min,temperature_2m_mean&"
            f"hourly=temperature_2m&"
            f"timezone=Europe/Warsaw"
        )
        try:
            with request.urlopen(url, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"HTTP error: {response.status}")
                data = response.read()
                self.stats = json.loads(data)
                self.stats["error"] = None
        except Exception as e:
            self.stats = {"error": f"Could not fetch weather data: {e}"}
    
    def get_tomorrow_temp(self):
        """Zwraca temperaturę na jutro."""
        if self.stats.get("error") is None and "daily" in self.stats:
            daily = self.stats["daily"]
            if len(daily.get("time", [])) > 1 and len(daily.get("temperature_2m_min", [])) > 1:
                return daily["time"][1], daily["temperature_2m_min"][1]
        return "Error", "Error"
    
    def return_for_simulation(self):
        """Zwraca dane pogodowe w formacie dla symulacji."""
        if self.stats.get("error") is None and "daily" in self.stats:
            daily = self.stats["daily"]
            return {
                "time": daily.get("time", []),
                "wind_speed_10m_max": daily.get("wind_speed_10m_max", []),
                "shortwave_radiation_sum": daily.get("shortwave_radiation_sum", []),
                "temperature_2m_max": daily.get("temperature_2m_max", []),
                "temperature_2m_min": daily.get("temperature_2m_min", []),
                "temperature_2m_mean": daily.get("temperature_2m_mean", []),
            }
        return None


def _quantize(value: float, digits: str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal(digits), rounding=ROUND_HALF_UP)


def _is_daytime(now_ts: int, sunrise: int | None, sunset: int | None) -> bool:
    if not sunrise or not sunset:
        return True
    return sunrise <= now_ts <= sunset


def _estimate_irradiance(cloud_pct: float, is_day: bool) -> float:
    if not is_day:
        return 0.0
    cloud_pct = max(0.0, min(100.0, cloud_pct))
    return 1000.0 * (1 - cloud_pct / 100.0)


def _pv_output_kw(pv_kwp: Decimal | None, irradiance_wm2: float) -> float:
    if not pv_kwp:
        return 0.0
    # kwp rated at 1000 W/m2
    return float(pv_kwp) * (irradiance_wm2 / 1000.0)


def _wind_output_kw(rated_kw: Decimal | None, wind_speed: float) -> float:
    if not rated_kw:
        return 0.0
    cut_in = 3.0
    rated_speed = 12.0
    cut_out = 25.0

    if wind_speed < cut_in or wind_speed >= cut_out:
        return 0.0
    if wind_speed >= rated_speed:
        return float(rated_kw)

    capacity = ((wind_speed - cut_in) / (rated_speed - cut_in)) ** 3
    capacity = max(0.0, min(1.0, capacity))
    return float(rated_kw) * capacity


def _generation_from_weather(weather: Dict[str, Any]) -> Dict[str, Decimal]:
    """
    Zwraca słownik z wartościami mocy (kW) dla PV, wiatru i sumy – bez zapisu do bazy.
    """
    now_ts = int(weather.get("dt", timezone.now().timestamp()))
    sunrise = weather.get("sys", {}).get("sunrise")
    sunset = weather.get("sys", {}).get("sunset")
    is_day = _is_daytime(now_ts, sunrise, sunset)

    temp_c = weather.get("main", {}).get("temp")
    wind_speed = float(weather.get("wind", {}).get("speed", 0.0))
    cloudiness = float(weather.get("clouds", {}).get("all", 0.0))
    irradiance = _estimate_irradiance(cloudiness, is_day)

    devices = SimDevice.objects.filter(status=SimDevice.Status.ACTIVE)
    pv_total = 0.0
    wind_total = 0.0

    for device in devices:
        if device.type_code == SimDevice.TypeCode.PV:
            pv_total += _pv_output_kw(device.pv_kwp, irradiance)
        elif device.type_code == SimDevice.TypeCode.WIND:
            wind_total += _wind_output_kw(device.wind_rated_kw, wind_speed)

    total_kw = pv_total + wind_total

    return {
        "pv_generation_kw": _quantize(pv_total, "0.001"),
        "wind_generation_kw": _quantize(wind_total, "0.001"),
        "total_generation_kw": _quantize(total_kw, "0.001"),
        "temperature_c": _quantize(temp_c, "0.01") if temp_c is not None else None,
        "wind_speed_ms": _quantize(wind_speed, "0.01"),
        "cloudiness_pct": int(cloudiness),
        "solar_irradiance_wm2": _quantize(irradiance, "0.01"),
        "timestamp": now_ts,
    }


def simulate_generation_from_weather(weather: Dict[str, Any]) -> GenerationHistory:
    now_ts = int(weather.get("dt", timezone.now().timestamp()))
    sunrise = weather.get("sys", {}).get("sunrise")
    sunset = weather.get("sys", {}).get("sunset")
    is_day = _is_daytime(now_ts, sunrise, sunset)

    temp_c = weather.get("main", {}).get("temp")
    wind_speed = float(weather.get("wind", {}).get("speed", 0.0))
    cloudiness = float(weather.get("clouds", {}).get("all", 0.0))
    irradiance = _estimate_irradiance(cloudiness, is_day)

    devices = SimDevice.objects.filter(status=SimDevice.Status.ACTIVE)
    pv_total = 0.0
    wind_total = 0.0

    for device in devices:
        if device.type_code == SimDevice.TypeCode.PV:
            pv_total += _pv_output_kw(device.pv_kwp, irradiance)
        elif device.type_code == SimDevice.TypeCode.WIND:
            wind_total += _wind_output_kw(device.wind_rated_kw, wind_speed)

    total_kw = pv_total + wind_total

    timestamp = timezone.datetime.fromtimestamp(now_ts, tz=timezone.utc)
    timestamp = timestamp.astimezone(timezone.get_current_timezone())

    entry = GenerationHistory.objects.create(
        timestamp=timestamp,
        location=LODZ_COORDS["label"],
        temperature_c=_quantize(temp_c, "0.01") if temp_c is not None else None,
        wind_speed_ms=_quantize(wind_speed, "0.01"),
        cloudiness_pct=int(cloudiness),
        solar_irradiance_wm2=_quantize(irradiance, "0.01"),
        pv_generation_kw=_quantize(pv_total, "0.001"),
        wind_generation_kw=_quantize(wind_total, "0.001"),
        total_generation_kw=_quantize(total_kw, "0.001"),
        weather_payload=weather,
    )

    return entry


def estimate_energy_kwh_for_forecast(forecast_list: Iterable[Dict[str, Any]]) -> Dict[str, Decimal]:
    """
    Przyjmuje listę prognoz (np. 3-godzinnych z /forecast) i zwraca energię w kWh.
    Zakłada stałą moc w trakcie przedziału prognozy.
    """
    pv_kwh = Decimal("0.000")
    wind_kwh = Decimal("0.000")
    total_kwh = Decimal("0.000")

    for item in forecast_list:
        # OpenWeather forecast ma dt (UTC) i 3h krok
        generation = _generation_from_weather(item)
        hours = Decimal("3")  # forecast endpoint to 3h step
        pv_kwh += generation["pv_generation_kw"] * hours
        wind_kwh += generation["wind_generation_kw"] * hours
        total_kwh += generation["total_generation_kw"] * hours

    return {
        "pv_energy_kwh": pv_kwh.quantize(Decimal("0.001")),
        "wind_energy_kwh": wind_kwh.quantize(Decimal("0.001")),
        "total_energy_kwh": total_kwh.quantize(Decimal("0.001")),
    }


def estimate_energy_kwh_from_hourly(hourly_list: Iterable[Dict[str, Any]]) -> Dict[str, Decimal]:
    """
    Dla danych historycznych (godzinowych) sumuje energię w kWh.
    """
    pv_kwh = Decimal("0.000")
    wind_kwh = Decimal("0.000")
    total_kwh = Decimal("0.000")

    for item in hourly_list:
        generation = _generation_from_weather(item)
        hours = Decimal("1")
        pv_kwh += generation["pv_generation_kw"] * hours
        wind_kwh += generation["wind_generation_kw"] * hours
        total_kwh += generation["total_generation_kw"] * hours

    return {
        "pv_energy_kwh": pv_kwh.quantize(Decimal("0.001")),
        "wind_energy_kwh": wind_kwh.quantize(Decimal("0.001")),
        "total_energy_kwh": total_kwh.quantize(Decimal("0.001")),
    }


def _convert_radiation_to_cloudiness(shortwave_radiation_sum: float) -> float:
    """
    Konwertuje sumę promieniowania słonecznego (MJ/m²) na procent zachmurzenia.
    Maksymalne promieniowanie dzienne to około 20-30 MJ/m² (czyste niebo).
    """
    if shortwave_radiation_sum is None:
        return 50.0  # Domyślnie 50% zachmurzenia
    
    # Normalizuj do zakresu 0-100%
    # Zakładamy maksymalne promieniowanie 25 MJ/m² dla czystego nieba
    max_radiation = 25.0
    cloudiness = max(0.0, min(100.0, 100.0 * (1.0 - (shortwave_radiation_sum / max_radiation))))
    return cloudiness


def generate_mock_weather(dt_ts: int | None = None) -> Dict[str, Any]:
    """
    Generuje pojedynczy punkt pogodowy używając Open-Meteo API.
    Jeśli API nie działa, zwraca mockowane dane.
    """
    if dt_ts is None:
        dt_ts = int(timezone.now().timestamp())
    
    # Próbuj pobrać prawdziwe dane z Open-Meteo
    try:
        weather_conn = WeatherConnection()
        weather_conn.connect()
        
        if weather_conn.stats.get("error") is None and "daily" in weather_conn.stats:
            daily = weather_conn.stats["daily"]
            times = daily.get("time", [])
            temps_mean = daily.get("temperature_2m_mean", [])
            wind_speeds = daily.get("wind_speed_10m_max", [])
            radiation = daily.get("shortwave_radiation_sum", [])
            
            # Znajdź najbliższą datę
            target_date = datetime.fromtimestamp(dt_ts, tz=timezone.get_current_timezone()).date()
            target_str = target_date.isoformat()
            
            if target_str in times:
                idx = times.index(target_str)
                temp = temps_mean[idx] if idx < len(temps_mean) else 15.0
                wind = wind_speeds[idx] if idx < len(wind_speeds) else 5.0
                rad = radiation[idx] if idx < len(radiation) else 10.0
                cloudiness = _convert_radiation_to_cloudiness(rad)
            else:
                # Jeśli nie ma dokładnej daty, użyj pierwszej dostępnej lub średniej
                temp = temps_mean[0] if temps_mean else 15.0
                wind = wind_speeds[0] if wind_speeds else 5.0
                rad = radiation[0] if radiation else 10.0
                cloudiness = _convert_radiation_to_cloudiness(rad)
            
            return {
                "dt": dt_ts,
                "sys": {"sunrise": None, "sunset": None},
                "main": {"temp": float(temp)},
                "wind": {"speed": float(wind)},
                "clouds": {"all": float(cloudiness)},
            }
    except Exception as e:
        # Fallback do mockowanych danych jeśli API nie działa
        pass
    
    # Fallback: mockowane dane
    return {
        "dt": dt_ts,
        "sys": {"sunrise": None, "sunset": None},
        "main": {"temp": random.uniform(-5, 25)},
        "wind": {"speed": random.uniform(0, 15)},
        "clouds": {"all": random.uniform(0, 100)},
    }


def generate_mock_series(start_dt: datetime, end_dt: datetime, step_hours: int = 24) -> List[Dict[str, Any]]:
    """
    Generuje serię pogodową używając Open-Meteo API.
    Jeśli API nie działa, używa mockowanych danych z dryfem +/-10%.
    """
    results: List[Dict[str, Any]] = []
    
    # Próbuj pobrać prawdziwe dane z Open-Meteo
    try:
        weather_conn = WeatherConnection()
        weather_conn.connect()
        
        if weather_conn.stats.get("error") is None and "daily" in weather_conn.stats:
            daily = weather_conn.stats["daily"]
            times = daily.get("time", [])
            temps_mean = daily.get("temperature_2m_mean", [])
            wind_speeds = daily.get("wind_speed_10m_max", [])
            radiation = daily.get("shortwave_radiation_sum", [])
            
            cur = start_dt
            while cur <= end_dt:
                cur_date_str = cur.date().isoformat()
                
                if cur_date_str in times:
                    idx = times.index(cur_date_str)
                    temp = temps_mean[idx] if idx < len(temps_mean) else 15.0
                    wind = wind_speeds[idx] if idx < len(wind_speeds) else 5.0
                    rad = radiation[idx] if idx < len(radiation) else 10.0
                    cloudiness = _convert_radiation_to_cloudiness(rad)
                else:
                    # Jeśli nie ma danych dla tej daty, użyj najbliższej dostępnej
                    if times:
                        # Użyj pierwszej dostępnej wartości
                        temp = temps_mean[0] if temps_mean else 15.0
                        wind = wind_speeds[0] if wind_speeds else 5.0
                        rad = radiation[0] if radiation else 10.0
                        cloudiness = _convert_radiation_to_cloudiness(rad)
                    else:
                        # Fallback
                        temp = 15.0
                        wind = 5.0
                        cloudiness = 50.0
                
                results.append({
                    "dt": int(cur.timestamp()),
                    "sys": {"sunrise": None, "sunset": None},
                    "main": {"temp": float(temp)},
                    "wind": {"speed": float(wind)},
                    "clouds": {"all": float(cloudiness)},
                })
                
                cur += timedelta(hours=step_hours)
            
            if results:
                return results
    except Exception as e:
        # Fallback do mockowanych danych jeśli API nie działa
        pass
    
    # Fallback: mockowane dane z dryfem
    base = generate_mock_weather(int(start_dt.timestamp()))
    results.append(base)
    
    cur = start_dt + timedelta(hours=step_hours)
    last = base
    while cur <= end_dt:
        def jitter(val: float) -> float:
            delta_pct = random.uniform(-0.1, 0.1)  # +/-10%
            return max(0.0, val * (1 + delta_pct))
        
        next_point = {
            "dt": int(cur.timestamp()),
            "sys": {"sunrise": None, "sunset": None},
            "main": {"temp": jitter(last["main"]["temp"])},
            "wind": {"speed": jitter(last["wind"]["speed"])},
            "clouds": {"all": min(100.0, jitter(last["clouds"]["all"]))},
        }
        results.append(next_point)
        last = next_point
        cur += timedelta(hours=step_hours)
    
    return results


# --- Battery helpers ---

def get_or_create_battery() -> BatteryState:
    battery, _ = BatteryState.objects.get_or_create(id=1, defaults={"max_capacity_kwh": Decimal("100.000")})
    return battery


def _log_battery(charge: Decimal, source: str):
    BatteryLog.objects.create(charge_kwh=charge, source=source)


def ensure_randomized_today() -> BatteryState:
    battery = get_or_create_battery()
    today = date.today()
    if battery.last_randomized_date != today:
        battery.current_charge_kwh = Decimal(str(random.uniform(0, float(battery.max_capacity_kwh)))).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )
        battery.last_randomized_date = today
        battery.save(update_fields=["current_charge_kwh", "last_randomized_date"])
        _log_battery(battery.current_charge_kwh, "randomized")
    return battery


def adjust_battery(action: str, amount_kwh: Decimal) -> BatteryState:
    if amount_kwh < 0:
        raise ValueError("amount_kwh must be non-negative")

    battery = ensure_randomized_today()

    if action == "add":
        battery.current_charge_kwh = min(
            battery.max_capacity_kwh,
            (battery.current_charge_kwh + amount_kwh).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        )
    elif action == "remove":
        battery.current_charge_kwh = max(
            Decimal("0.000"),
            (battery.current_charge_kwh - amount_kwh).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        )
    else:
        raise ValueError("action must be 'add' or 'remove'")

    battery.save(update_fields=["current_charge_kwh"])
    _log_battery(battery.current_charge_kwh, action)
    return battery

