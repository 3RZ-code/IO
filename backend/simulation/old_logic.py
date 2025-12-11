"""from decimal import Decimal
from .models import SimDevice

#IMPORT POGODY
try:
    from optimization_control.weather import weather_connection
    from optimization_control.models import Device as OptDevice

    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False
    print("UWAGA: Nie znaleziono modułu 'optimization_control'. Symulacja nie zaktualizuje bazy.")


class SimulationLogic:

    @staticmethod
    def calculate_pv_production(radiation_sum, capacity_kwp):
        """
        Liczy prąd z fotowoltaiki.
        radiation_sum: MJ/m2 (z OpenMeteo)
        """
        if not capacity_kwp or capacity_kwp <= 0:
            return Decimal("0.0000")

        # Uproszczony przelicznik: Promieniowanie * Moc * Współczynnik
        # Zakładamy, że radiation_sum to energia dzienna, więc dzielimy, by uzyskać chwilową moc (uproszczenie)
        factor = Decimal(str(radiation_sum)) * Decimal("0.05")
        production = capacity_kwp * factor
        return round(production, 4)

    @staticmethod
    def calculate_wind_production(wind_speed, rated_power):
        """
        Liczy prąd z wiatraka.
        wind_speed: km/h
        """
        if not rated_power or rated_power <= 0:
            return Decimal("0.0000")

        ws = float(wind_speed)

        # Turbina startuje przy 10 km/h, max moc przy 45 km/h
        if ws < 10:
            return Decimal("0.0000")
        elif ws >= 45:
            return Decimal(rated_power)
        else:
            # Liniowy wzrost mocy
            ratio = (ws - 10) / (35)
            return Decimal(rated_power) * Decimal(ratio)

    @staticmethod
    def run_simulation(manual_weather=None):
        """
        Główna funkcja uruchamiająca symulację.
        """
        weather_data = {}

        # 1. POBIERANIE POGODY
        if manual_weather:
            # Tryb Ręczny
            weather_data = manual_weather
            print(f"[SYMULACJA] Tryb ręczny: {weather_data}")
        elif OPTIMIZATION_AVAILABLE:
            # Tryb Live
            try:
                wc = weather_connection()
                wc.connect()
                data = wc.return_for_simulation()

                # Wyciągamy dane na jutro (indeks 1)
                weather_data = {
                    'sun': data.get('shortwave_radiation_sum', [0, 0])[1],
                    'wind': data.get('wind_speed_10m_max', [0, 0])[1],
                    'temp': data.get('temperature_2m_mean', [0, 0])[1]
                }
                print(f"[SYMULACJA] Pogoda od weather: {weather_data}")
            except Exception as e:
                return {"error": f"Błąd połączenia z pogodą: {str(e)}"}
        else:
            return {"error": "Brak pogody (API niedostępne i brak danych ręcznych)"}

        # 2. OBLICZENIA I ZAPIS
        devices = SimDevice.objects.filter(status=SimDevice.Status.ACTIVE)
        updated_count = 0

        # pobranie wartości (z domyślnym 0)
        sun_val = weather_data.get('sun', 0)
        wind_val = weather_data.get('wind', 0)
        temp_val = weather_data.get('temp', 20)

        results_log = []

        for dev in devices:
            new_power = Decimal("0.0000")

            # Fotowoltaika
            if dev.type_code == SimDevice.TypeCode.PV:
                new_power = SimulationLogic.calculate_pv_production(sun_val, dev.pv_kwp)

            # Wiatraki
            elif dev.type_code == SimDevice.TypeCode.WIND:
                new_power = SimulationLogic.calculate_wind_production(wind_val, dev.wind_rated_kw)

            # Pompy Ciepła (Zużycie)
            elif dev.type_code == SimDevice.TypeCode.HP:
                base_power = Decimal("2.0")
                if temp_val < 0:
                    new_power = base_power * Decimal("1.5")
                elif temp_val < 15:
                    new_power = base_power * Decimal("1.2")
                else:
                    new_power = base_power * Decimal("0.5")

            # Zapis u nas
            dev.power_kw = new_power
            dev.save()

            # 3. AKTUALIZACJA TABELI (OptDevice)
            synced = False
            if OPTIMIZATION_AVAILABLE:
                try:
                    # Szukamy urządzenia o tej samej nazwie
                    opt_dev = OptDevice.objects.get(name=dev.name)
                    opt_dev.power = float(new_power)

                    # Logika włączenia: jeśli produkuje prąd, to jest ACTIVE
                    if new_power > 0:
                        opt_dev.status = True

                    opt_dev.save()
                    synced = True
                except OptDevice.DoesNotExist:
                    pass  # Nie ma urządzenia

            results_log.append({
                "device": dev.name,
                "power": float(new_power),
                "synced": synced
            })
            updated_count += 1

        return {
            "status": "success",
            "weather_used": weather_data,
            "updated_devices": updated_count,
            "details": results_log
        }"""