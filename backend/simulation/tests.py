from django.test import TestCase
from decimal import Decimal
from unittest.mock import patch, MagicMock
from .models import SimDevice
from .logic import SimulationLogic


class SimulationSimpleTestCase(TestCase):

    def setUp(self):
        """
        Przygotowanie czystej bazy przed każdym testem.
        """
        # 1. Czyścimy śmieci z migracji (CSV)
        SimDevice.objects.all().delete()

        # 2. Tworzymy nasze urządzenia testowe
        SimDevice.objects.create(
            device_id="TEST_PV",
            type_code=SimDevice.TypeCode.PV,
            name="Panel Testowy",
            status=SimDevice.Status.ACTIVE,
            pv_kwp=Decimal("10.0000"),
            power_kw=Decimal("0.0000")
        )

        SimDevice.objects.create(
            device_id="TEST_WIND",
            type_code=SimDevice.TypeCode.WIND,
            name="Wiatrak Testowy",
            status=SimDevice.Status.ACTIVE,
            wind_rated_kw=Decimal("10.0000"),
            power_kw=Decimal("0.0000")
        )

    def test_math_synthetic_mode(self):
        """
        Sprawdza czy tryb 'z palca' (1-10) mnoży poprawnie.
        PV: mnożnik x2.0
        WIND: mnożnik x3.0
        """
        # Test dla PV (Input 5 -> Oczekujemy 10 kW)
        power_pv, time_pv = SimulationLogic.calculate_pv_simple(5, is_synthetic=True)
        self.assertEqual(power_pv, Decimal("10.00"))

        # Test dla Wiatraka (Input 5 -> Oczekujemy 15 kW)
        power_wind, time_wind = SimulationLogic.calculate_wind_simple(5, is_synthetic=True)
        self.assertEqual(power_wind, Decimal("15.00"))

        # Sprawdzamy czy zwraca godzinę (np. kończy się na :00)
        self.assertTrue(time_pv.endswith(":00"))

    def test_math_api_mode(self):
        """
        Sprawdza czy tryb 'z API' (duże liczby) używa mniejszych mnożników.
        PV: mnożnik x0.5
        WIND: mnożnik x0.2
        """
        # Test dla PV (Input 100 jednostek słońca -> Oczekujemy 50 kW)
        power_pv, time_pv = SimulationLogic.calculate_pv_simple(100, is_synthetic=False)
        self.assertEqual(power_pv, Decimal("50.00"))

        # Test dla Wiatraka (Input 100 km/h -> Oczekujemy 20 kW)
        power_wind, time_wind = SimulationLogic.calculate_wind_simple(100, is_synthetic=False)
        self.assertEqual(power_wind, Decimal("20.00"))

    def test_run_simulation_synthetic(self):
        """
        Testuje całą pętlę symulacji w trybie ręcznym (wpisujemy pogodę z palca).
        Sprawdza czy dane zapisały się w bazie.
        """
        manual_weather = {'sun': 4, 'wind': 2}  # PV: 4*2=8, WIND: 2*3=6

        # Uruchamiamy
        result = SimulationLogic.run_simulation(manual_weather=manual_weather)

        # Sprawdzamy status
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['mode'], 'synthetic')
        self.assertEqual(result['updated'], 2)  # Zaktualizowano 2 urządzenia

        # Sprawdzamy bazę danych
        pv = SimDevice.objects.get(device_id="TEST_PV")
        wind = SimDevice.objects.get(device_id="TEST_WIND")

        self.assertEqual(pv.power_kw, Decimal("8.00"))  # 4 * 2.0
        self.assertEqual(wind.power_kw, Decimal("6.00"))  # 2 * 3.0

    @patch('simulation.logic.weather_connection')
    def test_run_simulation_api_mock(self, mock_weather_cls):
        """
        Testuje symulację w trybie API, ale bez prawdziwego łączenia z internetem.
        Udajemy (mockujemy), że kolega przesłał nam dane.
        """
        # 1. Konfigurujemy fałszywą pogodę od kolegi
        mock_instance = mock_weather_cls.return_value
        mock_instance.return_for_simulation.return_value = {
            'shortwave_radiation_sum': [200],  # index 0 - Słońce
            'wind_speed_10m_max': [50],  # index 0 - Wiatr
            'temperature_2m_mean': [15]
        }

        # 2. Uruchamiamy symulację (bez manual_weather -> więc weźmie API)
        result = SimulationLogic.run_simulation(manual_weather=None)

        # 3. Sprawdzamy
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['mode'], 'api')

        pv = SimDevice.objects.get(device_id="TEST_PV")
        # PV logic (API): 200 * 0.5 = 100
        self.assertEqual(pv.power_kw, Decimal("100.00"))