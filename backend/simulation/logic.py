from decimal import Decimal
from django.utils import timezone
from .models import SimDevice

# --- IMPORT MODUŁÓW (OPTYMALIZACJA) ---
try:
    from optimization_control.weather import weather_connection
    from optimization_control.models import Device as OptDevice

    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False
    print("UWAGA: Nie znaleziono modułu 'optimization_control'. Działam w trybie izolowanym.")


class SimulationLogic:

    @staticmethod
    def get_current_rounded_hour():
        """
        Pomocnicza funkcja: Zwraca aktualną godzinę zaokrągloną do pełnej (np. "14:00").
        """
        now = timezone.now()
        rounded_time = now.replace(minute=0, second=0, microsecond=0)
        return rounded_time.strftime("%H:%M")

    @staticmethod
    def calculate_pv_simple(sun_input, is_synthetic=False):
        """
        Liczy prąd z fotowoltaiki.
        Zwraca: (Moc w kW, Godzina string)
        """
        current_hour = SimulationLogic.get_current_rounded_hour()

        value = Decimal(str(sun_input))

        if is_synthetic:
            # TRYB SYNTETYCZNY (Skala 1-10)
            # Np. wpiszesz 5 -> wyjdzie 10 kW (mnożnik x2)
            production = value * Decimal("2.0")
        else:
            # TRYB API (Dane pogodowe np. 15 MJ/m2)
            # Prosty mnożnik, żeby wyszły sensowne liczby
            production = value * Decimal("0.5")

        # Zabezpieczenie przed ujemnymi
        if production < 0: production = Decimal("0.00")

        return round(production, 2), current_hour

    @staticmethod
    def calculate_wind_simple(wind_input, is_synthetic=False):
        """
        Liczy prąd z wiatraka.
        Zwraca: (Moc w kW, Godzina string)
        """
        current_hour = SimulationLogic.get_current_rounded_hour()

        value = Decimal(str(wind_input))

        if is_synthetic:
            # TRYB SYNTETYCZNY (Skala 1-10)
            # Np. wpiszesz 5 -> wyjdzie 15 kW (mnożnik x3)
            production = value * Decimal("3.0")
        else:
            # TRYB API (Wiatr w km/h, np. 20 km/h)
            production = value * Decimal("0.2")

        if production < 0: production = Decimal("0.00")

        return round(production, 2), current_hour

    # =========================================================
    # ZAKOMENTOWANA POMPA CIEPŁA (Na przyszłość)
    # =========================================================
    # @staticmethod
    # def calculate_heat_simple(temp_input, is_synthetic=False):
    #     """
    #     Zwraca zużycie prądu przez pompę (kW) i godzinę.
    #     """
    #     current_hour = SimulationLogic.get_current_rounded_hour()
    #     val = Decimal(str(temp_input))
    #
    #     # Prosta logika: im zimniej (mniejsza wartość), tym większe zużycie
    #     # Np. temp 20 -> zużycie 1 kW
    #     # temp -5 -> zużycie 5 kW
    #     consumption = Decimal("5.0") - (val * Decimal("0.2"))
    #     if consumption < 0: consumption = Decimal("0.5") # Min zużycie
    #
    #     return round(consumption, 2), current_hour

    @staticmethod
    def run_simulation(manual_weather=None):
        """
        Zarządza pobieraniem danych i aktualizacją baz kolegów.
        manual_weather: słownik np. {'sun': 5, 'wind': 8} (Skala 1-10)
        """

        # 1. DECYZJA: Skąd bierzemy dane?
        is_synthetic_mode = False
        weather_data = {}

        if manual_weather:
            # --- TRYB RĘCZNY (1-10) ---
            is_synthetic_mode = True
            weather_data = manual_weather
            print(f"[SYMULACJA] Tryb Ręczny (1-10): {weather_data}")

        elif OPTIMIZATION_AVAILABLE:
            # --- TRYB API (WEATHER.PY) ---
            try:
                wc = weather_connection()
                wc.connect()  # Pobiera z neta
                data = wc.return_for_simulation()  # Pobiera słownik z weather.py

                # Bierzemy dane na DZIŚ (indeks 0), żeby pasowało do "aktualnej godziny"
                weather_data = {
                    'sun': data.get('shortwave_radiation_sum', [0])[0],
                    'wind': data.get('wind_speed_10m_max', [0])[0],
                    'temp': data.get('temperature_2m_mean', [0])[0]
                }
                print(f"[SYMULACJA] Tryb API: {weather_data}")
            except Exception as e:
                return {"error": f"Błąd API pogody: {e}"}
        else:
            return {"error": "Brak API i brak danych ręcznych."}

        # 2. OBLICZENIA I AKTUALIZACJA
        devices = SimDevice.objects.filter(status=SimDevice.Status.ACTIVE)
        updated_count = 0
        results_log = []

        # Pobieramy wartości (domyślnie 0 jak czegoś brak)
        sun_val = weather_data.get('sun', 0)
        wind_val = weather_data.get('wind', 0)
        # temp_val = weather_data.get('temp', 15) # Na razie nieużywane

        for dev in devices:
            # Tu wpadnie (Moc, Godzina)
            calculated_power = Decimal("0.00")
            time_info = ""

            # --- A. FOTOWOLTAIKA ---
            if dev.type_code == SimDevice.TypeCode.PV:
                calculated_power, time_info = SimulationLogic.calculate_pv_simple(
                    sun_val, is_synthetic=is_synthetic_mode
                )

            # --- B. WIATRAK ---
            elif dev.type_code == SimDevice.TypeCode.WIND:
                calculated_power, time_info = SimulationLogic.calculate_wind_simple(
                    wind_val, is_synthetic=is_synthetic_mode
                )

            # --- C. POMPA (Zakomentowana logika) ---
            # elif dev.type_code == SimDevice.TypeCode.HP:
            #     calculated_power, time_info = SimulationLogic.calculate_heat_simple(
            #         temp_val, is_synthetic=is_synthetic_mode
            #     )

            # 3. ZAPIS DO NASZEJ BAZY
            dev.power_kw = calculated_power
            dev.save()

            # 4. ZAPIS DO BAZY KOLEGI (Żeby Optymalizacja to widziała)
            synced = False
            if OPTIMIZATION_AVAILABLE:
                try:
                    opt_dev = OptDevice.objects.get(name=dev.name)
                    opt_dev.power = float(calculated_power)

                    # Jeśli produkuje prąd -> ustawiamy status True (aktywny)
                    if calculated_power > 0:
                        opt_dev.status = True

                    # Możesz tu też zapisać godzinę jeśli kolega ma na to pole w bazie
                    # opt_dev.current_hours = time_info

                    opt_dev.save()
                    synced = True
                except OptDevice.DoesNotExist:
                    pass

            results_log.append({
                "device": dev.name,
                "power": float(calculated_power),
                "time": time_info,
                "synced": synced
            })
            updated_count += 1

        return {
            "status": "success",
            "mode": "synthetic" if is_synthetic_mode else "api",
            "updated": updated_count,
            "data": results_log
        }