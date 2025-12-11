# Simulation module – przewodnik krok po kroku (dla totalnych początkujących)

Moduł symuluje produkcję energii, stan baterii oraz sztuczne dane pogodowe. Działa **offline** (mocki), bez zewnętrznych kluczy i API.

---
## Jak to zostało zrobione (żebyś sam umiał to powtórzyć)
1) **Modele** (`models.py`):
   - `SimDevice`: wirtualne urządzenia (typ PV/WIND/…). Trzymamy ich parametry mocy (`pv_kwp`, `wind_rated_kw`).
   - `GenerationHistory`: zapis pojedynczej symulacji (czas, pogoda, PV, wiatr, suma, payload pogody).
   - `BatteryState`: aktualny stan baterii (max capacity, current charge, data ostatniego losowania).
   - `BatteryLog`: log każdej zmiany w baterii (timestamp, charge, źródło).

2) **Mock pogody** (`services.py`):
   - Funkcje `generate_mock_weather` i `generate_mock_series` tworzą losowe punkty pogodowe. Każdy kolejny punkt to poprzedni ±10% (dryf).
   - Brak połączeń do internetu; wszystko powstaje lokalnie.

3) **Symulacja produkcji** (`services.py`):
   - Dla PV: moc ~ irradiance (0–1000 W/m²) * `pv_kwp` / 1000.
   - Dla wiatru: prosta krzywa mocy z progami cut-in (3 m/s), rated (12 m/s), cut-out (25 m/s).
   - Wynik zapisujemy w `GenerationHistory` (PV, wiatr, suma).

4) **Bateria** (`services.py`):
   - Przy pierwszym wywołaniu po północy losuje nowy stan (0…max_capacity).
   - `adjust_battery` dodaje/odejmuje energię, pilnuje zakresu 0…max.
   - Każda zmiana jest logowana w `BatteryLog`.

5) **Widoki/endpointy** (`views.py`, `urls.py`):
   - Każdy endpoint korzysta z powyższych funkcji; formaty JSON są proste (patrz niżej).

6) **Jak dodać to u siebie**:
   - Utwórz modele jak wyżej, zarejestruj w adminie (opcjonalnie).
   - Napisz funkcje generujące dane (mock) i obliczające moce.
   - Zrób widoki DRF/APIView, mapuj w `urls.py`.
   - Dodaj migracje i uruchom `migrate`.

---
## Endpointy (co robią i jak je wywołać)
Base URL: `/simulation/`

### Urządzenia
- `GET /simulation/devices/` – lista urządzeń (`SimDevice`).

### Generacja energii
- `POST /simulation/generation/run/`  
  Jedna symulacja na losowej pogodzie. Body puste.

- `POST /simulation/generation/run-range/`  
  Wiele symulacji w zakresie dat.  
  Przykład body:
  ```json
  {
    "start": "2025-01-01",
    "end": "2025-01-03",
    "step_hours": 3
  }
  ```
  - `start`/`end`: `YYYY-MM-DD` (koniec to end+23:59:59).  
  - `step_hours` domyślnie 3.

- `GET /simulation/generation/` – lista historii.  
- `GET /simulation/generation/<id>/` – pojedynczy wpis.

### Energia (mock)
- `GET /simulation/generation/forecast/today/`  
  Energia kWh na dziś (mockowana seria co 3h).

- `GET /simulation/generation/forecast/last-month/`  
  Suma z zapisanych symulacji z ostatnich 30 dni. Jeśli brak danych → 404 (uruchom `generation/run`).

### Pogoda (mock)
- `GET /simulation/weather/mock/?start=YYYY-MM-DD&end=YYYY-MM-DD`  
  Punkty co 24h, każdy kolejny to poprzedni ±10%. Pola: temp, wind, clouds, dt.

### Bateria
- `GET /simulation/battery/`  
  Zwraca stan; pierwsze wywołanie po północy losuje nowy stan 0…max.

- `POST /simulation/battery/`  
  Body: `{"action": "add", "amount_kwh": 5}` lub `{"action": "remove", "amount_kwh": 2}`.  
  Zwraca zaktualizowany stan.

- `GET /simulation/battery/history/`  
  Log zmian (`timestamp`, `charge_kwh`, `source`).

---
## Co się dzieje pod spodem (ważne detale)
- Wszystko jest w strefie `TIME_ZONE` z ustawień Django.  
- Kwantyzacja liczb: kW/kWh do 3 miejsc, temp/irradiance do 2 miejsc.  
- Brak aktywnych `SimDevice` ⇒ produkcja = 0.  
- Mock pogody ma dryf ±10% między punktami, krok zależny od endpointu (3h lub 24h).
- Bateria loguje każdą zmianę (losowanie, add/remove), więc możesz śledzić pełną historię.

---
## Jak to uruchomić od zera (praktyczne kroki)
1. Migracje (nowe modele baterii/logów):  
   ```
   python manage.py makemigrations simulation
   python manage.py migrate
   ```
2. Dodaj urządzenia `SimDevice` (admin lub ORM); ustaw `status=active` i parametry mocy (`pv_kwp`, `wind_rated_kw`).
3. Wygeneruj dane:
   - Jednorazowo: `POST /simulation/generation/run/`
   - Hurtowo: `POST /simulation/generation/run-range/` (np. 30 dni, co 3h).
4. Sprawdź:
   - Historia: `GET /simulation/generation/`
   - Energia 30 dni: `GET /simulation/generation/forecast/last-month/`
   - Bateria: `GET /simulation/battery/`, modyfikuj `POST /simulation/battery/`, log `GET /simulation/battery/history/`.
5. Testuj pogodę: `GET /simulation/weather/mock/?start=2025-01-01&end=2025-01-05`.

---
## Typowe scenariusze
- **Uzupełnij historię do raportu 30-dniowego**: `run-range` na 30 dni (krok 3h) → potem `forecast/last-month`.
- **Zużyj baterię do zera**: `GET /battery/` (wylosuje stan), kilka `POST remove`, historia w `/battery/history/`.
- **Sprawdź dzień produkcji**: `run-range` z `start=end=YYYY-MM-DD`, krok 3h → patrz `GenerationHistory`.

---
## Minimalny know-how do odtworzenia
1. Utwórz modele: urządzenia, historia generacji, bateria, log baterii.  
2. Napisz generator mock pogody (startowy punkt + dryf ±10%, krok 3h/24h).  
3. Napisz kalkulator mocy PV (proporcja do irradiance) i wiatru (krzywa mocy).  
4. Zrób endpointy DRF, które:
   - generują pogodę, liczą moce, zapisują do bazy,
   - zwracają sumy/raporty,
   - zarządzają stanem baterii z logowaniem.  
5. Przetestuj w Postman/cURL według przykładów powyżej.

