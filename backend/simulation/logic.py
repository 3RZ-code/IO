from decimal import Decimal
from django.utils import timezone
from .models import SimDevice

# --- 1. IMPORT POGODY (TYLKO LOKALNY PLIK) ---
try:
    # Importujemy tylko Twój plik z tego samego folderu
    from .weather_sim import weather_connection
    WEATHER_AVAILABLE = True
except ImportError:
    WEATHER_AVAILABLE = False
    print("UWAGA: Nie znaleziono pliku 'weather_sim.py' w folderze simulation.")


class SimulationLogic:

    @staticmethod
    def get_current_rounded_hour():
        """
        Zwraca aktualną godzinę zaokrągloną do pełnej (np. "14:00").
        """
        now = timezone.now()
        rounded_time = now.replace(minute=0, second=0, microsecond=0)
        return rounded_time.strftime("%H:%M")

    @staticmethod
    def calculate_pv_simple(sun_input, is_synthetic=False):
        """
        Liczy prąd z fotowoltaiki.
        """
        current_hour = SimulationLogic.get_current_rounded_hour()
        value = Decimal(str(sun_input))

        if is_synthetic:
            # Tryb Ręczny (1-10) -> x2
            production = value * Decimal("2.0")
        else:
            # Tryb API (MJ/m2) -> x0.5
            production = value * Decimal("0.5")

        if production < 0: production = Decimal("0.00")
        return round(production, 2), current_hour

    @staticmethod
    def calculate_wind_simple(wind_input, is_synthetic=False):
        """
        Liczy prąd z wiatraka.
        """
        current_hour = SimulationLogic.get_current_rounded_hour()
        value = Decimal(str(wind_input))

        if is_synthetic:
            # Tryb Ręczny (1-10) -> x3
            production = value * Decimal("3.0")
        else:
            # Tryb API (km/h) -> x0.2
            production = value * Decimal("0.2")

        if production < 0: production = Decimal("0.00")
        return round(production, 2), current_hour


    @staticmethod
    def run_simulation(manual_weather=None):
        """
        Główna pętla symulacji.
        """
        is_synthetic_mode = False
        weather_data = {}

        # --- 1. POBIERANIE DANYCH ---
        if manual_weather:
            # Tryb Ręczny
            is_synthetic_mode = True
            weather_data = manual_weather
            print(f"[SYMULACJA] Tryb Ręczny: {weather_data}")

        elif WEATHER_AVAILABLE:
            # Tryb API (z weather_sim.py)
            try:
                wc = weather_connection()
                wc.connect()
                data = wc.return_for_simulation()

                weather_data = {
                    'sun': data.get('shortwave_radiation_sum', [0])[0],
                    'wind': data.get('wind_speed_10m_max', [0])[0],
                    'temp': data.get('temperature_2m_mean', [0])[0]
                }
                print(f"[SYMULACJA] Tryb API: {weather_data}")
            except Exception as e:
                return {"error": f"Błąd w weather_sim: {e}"}
        else:
            return {"error": "Brak pliku pogody i brak danych ręcznych."}

        # --- 2. OBLICZENIA ---
        devices = SimDevice.objects.filter(status=SimDevice.Status.ACTIVE)
        updated_count = 0
        results_log = []

        sun_val = weather_data.get('sun', 0)
        wind_val = weather_data.get('wind', 0)

        for dev in devices:
            calculated_power = Decimal("0.00")
            time_info = ""

            # A. Fotowoltaika
            if dev.type_code == SimDevice.TypeCode.PV:
                calculated_power, time_info = SimulationLogic.calculate_pv_simple(
                    sun_val, is_synthetic=is_synthetic_mode
                )

            # B. Wiatrak
            elif dev.type_code == SimDevice.TypeCode.WIND:
                calculated_power, time_info = SimulationLogic.calculate_wind_simple(
                    wind_val, is_synthetic=is_synthetic_mode
                )

            # C. Zapisz tylko u nas (baza symulacji)
            dev.power_kw = calculated_power
            dev.save()

            # D. Dodaj do logów
            results_log.append({
                "device": dev.name,
                "power": float(calculated_power),
                "time": time_info,
                "synced": False # Zawsze False, bo wyłączyliśmy synchronizację
            })
            updated_count += 1

        return {
            "status": "success",
            "mode": "synthetic" if is_synthetic_mode else "api",
            "updated": updated_count,
            "data": results_log
        }