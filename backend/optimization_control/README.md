# Optimization Control - Dokumentacja Endpointu

## 📍 Endpoint

**URL:** `POST /optimization-control/`

## 🎯 Cel

Endpoint generuje **optymalny harmonogram włączania urządzeń** na podstawie:
- Priorytetów urządzeń
- Dostępności baterii
- Taryf energetycznych (off-peak vs peak)
- Produkcji energii z modułu `simulation`

## 📥 Request

### Metoda: `POST`

### Body (opcjonalne):

```json
{
  "start": "2025-01-01T00:00:00",
  "end": "2025-01-02T00:00:00"
}
```

**Parametry:**
- `start` (opcjonalny) - Data rozpoczęcia w formacie ISO: `YYYY-MM-DDTHH:MM:SS`
- `end` (opcjonalny) - Data zakończenia w formacie ISO: `YYYY-MM-DDTHH:MM:SS`

**Jeśli nie podasz dat:**
- Domyślnie: od teraz do +24h

### Przykład bez parametrów:

```bash
POST http://localhost:6543/optimization-control/
Content-Type: application/json

{}
```

### Przykład z datami:

```bash
POST http://localhost:6543/optimization-control/
Content-Type: application/json

{
  "start": "2025-12-12T00:00:00",
  "end": "2025-12-13T00:00:00"
}
```

## 📤 Response

### Sukces (200 OK):

```json
{
  "window": {
    "start": "2025-12-12T00:00:00+01:00",
    "end": "2025-12-13T00:00:00+01:00"
  },
  "summary": {
    "devices": 5,
    "total_demand_kwh": 12.5,
    "generation_kw_window_sum": 45.2,
    "battery_start_kwh": 50.0,
    "battery_used_kwh": 12.5,
    "battery_remaining_kwh": 37.5
  },
  "schedule": [
    {
      "device_id": 1,
      "device_name": "Klimatyzacja",
      "priority": 0,
      "power_kw": 2.5,
      "start": "2025-12-12T06:00:00+01:00",
      "end": "2025-12-12T07:00:00+01:00",
      "tariff": "peak",
      "energy_kwh": 2.5,
      "battery_used_kwh": 2.5,
      "source": "battery+grid"
    },
    {
      "device_id": 2,
      "device_name": "Pralka",
      "priority": 2,
      "power_kw": 1.0,
      "start": "2025-12-12T22:00:00+01:00",
      "end": "2025-12-12T23:00:00+01:00",
      "tariff": "offpeak",
      "energy_kwh": 1.0,
      "battery_used_kwh": 0.0,
      "source": "offpeak_grid"
    }
  ],
  "assumptions": {
    "offpeak_hours": [0, 1, 2, 3, 4, 5, 22, 23],
    "duration_h_default": 1,
    "priority_rule": "priorytet >=3 -> offpeak jeśli dostępne; mniejszy -> ASAP",
    "power_kw_source": "metric=='power_kw' z DeviceReading lub 1.0 gdy brak",
    "priority_source": "Device.priority (0-2) lub 5 gdy brak"
  }
}
```

### Błędy:

**400 Bad Request:**
```json
{
  "detail": "start/end w formacie YYYY-MM-DDTHH:MM:SS"
}
```

**404 Not Found:**
```json
{
  "detail": "Brak aktywnych urządzeń w data_acquisition.Device"
}
```

## 🔧 Jak Działa Algorytm

### Krok 1: Pobranie Danych

1. **Urządzenia** - Pobiera wszystkie aktywne urządzenia z `data_acquisition.Device`
2. **Moc urządzeń** - Dla każdego urządzenia szuka ostatniego odczytu `power_kw` w `DeviceReading`
3. **Priorytet** - Pobiera z `Device.priority` (0-2, gdzie 0 = najwyższy priorytet)
4. **Bateria** - Pobiera aktualny stan z `simulation.BatteryState`
5. **Produkcja** - Sumuje produkcję energii z `simulation.GenerationHistory` w oknie czasowym

### Krok 2: Definicja Taryf

**Off-Peak (tańsze godziny):** 22:00 - 05:59 (noc)
- Godziny: `[22, 23, 0, 1, 2, 3, 4, 5]`

**Peak (droższe godziny):** 06:00 - 21:59 (dzień)
- Wszystkie pozostałe godziny

### Krok 3: Sortowanie Urządzeń

Urządzenia są sortowane **rosnąco po priorytecie**:
- Priorytet 0 (najwyższy) → uruchamiane najpierw
- Priorytet 1 → następne
- Priorytet 2 (najniższy) → na końcu

### Krok 4: Harmonogramowanie

Dla każdego urządzenia:

1. **Wybór slotu czasowego:**
   - Jeśli `priority >= 3` → próbuje umieścić w **off-peak** (jeśli dostępne)
   - Jeśli `priority < 3` → umieszcza w **peak** (ASAP)
   - Jeśli brak slotów peak → używa off-peak
   - Jeśli brak wszystkich slotów → używa ostatniego dostępnego

2. **Użycie baterii:**
   - Najpierw zużywa energię z baterii
   - Jeśli bateria się wyczerpie → przechodzi na sieć
   - `battery_used_kwh` = min(pozostała bateria, zapotrzebowanie urządzenia)

3. **Źródło energii:**
   - `"battery+grid"` - jeśli użyto baterii
   - `"offpeak_grid"` - jeśli tylko sieć w godzinach off-peak
   - `"peak_grid"` - jeśli tylko sieć w godzinach peak

### Krok 5: Obliczenia

- **total_demand_kwh** - Suma zapotrzebowania wszystkich urządzeń
- **battery_used_kwh** - Całkowita energia zużyta z baterii
- **battery_remaining_kwh** - Pozostała energia w baterii

## 📊 Przykłady Użycia

### Przykład 1: Optymalizacja na dziś

```bash
curl -X POST http://localhost:6543/optimization-control/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Przykład 2: Optymalizacja na konkretny zakres

```bash
curl -X POST http://localhost:6543/optimization-control/ \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-12-12T00:00:00",
    "end": "2025-12-13T00:00:00"
  }'
```

### Przykład 3: W Swagger UI

1. Otwórz: `http://localhost:6543/swagger/`
2. Znajdź endpoint: `POST /optimization-control/`
3. Kliknij "Try it out"
4. Wpisz body (lub zostaw puste `{}`)
5. Kliknij "Execute"

## 🎓 Logika Priorytetów

### Priorytet 0 (Najwyższy)
- **Przykłady:** Klimatyzacja, ogrzewanie, lodówka
- **Harmonogram:** ASAP w godzinach peak
- **Cel:** Komfort i bezpieczeństwo

### Priorytet 1 (Średni)
- **Przykłady:** Oświetlenie, komputer
- **Harmonogram:** ASAP w godzinach peak
- **Cel:** Podstawowe funkcje

### Priorytet 2 (Niski)
- **Przykłady:** Pralka, zmywarka, ładowarka
- **Harmonogram:** Off-peak jeśli dostępne
- **Cel:** Oszczędność kosztów

### Priorytet >= 3 (Bardzo niski)
- **Przykłady:** Urządzenia bez priorytetu (domyślnie 5)
- **Harmonogram:** Zawsze off-peak
- **Cel:** Maksymalna oszczędność

## 🔋 Zarządzanie Baterią

1. **Bateria jest używana w pierwszej kolejności** - aż do wyczerpania
2. **Każde urządzenie** zużywa z baterii tyle, ile może (do zapotrzebowania)
3. **Reszta** jest pobierana z sieci
4. **Bateria nie może być ujemna** - jeśli się wyczerpie, wszystko idzie z sieci

## ⚙️ Założenia i Ograniczenia

### Założenia:
- Każde urządzenie działa **1 godzinę** (domyślnie)
- Moc urządzenia: z `DeviceReading` (metric='power_kw') lub 1.0 kW domyślnie
- Priorytet: z `Device.priority` (0-2) lub 5 domyślnie

### Ograniczenia:
- **Nie obsługuje** urządzeń działających dłużej niż 1h
- **Nie uwzględnia** prognozy produkcji energii (tylko historia)
- **Nie optymalizuje** kolejności w ramach tego samego priorytetu
- **Nie uwzględnia** czasu włączenia/wyłączenia urządzeń

## 🔍 Debugowanie

### Sprawdź czy masz urządzenia:

```python
# W Django shell
from data_acquisition.models import Device
Device.objects.filter(is_active=True).count()
```

### Sprawdź stan baterii:

```python
from simulation.models import BatteryState
battery = BatteryState.objects.get(id=1)
print(f"Bateria: {battery.current_charge_kwh}/{battery.max_capacity_kwh} kWh")
```

### Sprawdź produkcję energii:

```python
from simulation.models import GenerationHistory
from django.utils import timezone
from datetime import timedelta

start = timezone.now()
end = start + timedelta(hours=24)
gen = GenerationHistory.objects.filter(timestamp__gte=start, timestamp__lt=end)
print(f"Produkcja: {sum(g.total_generation_kw for g in gen)} kW")
```

## 📝 Podsumowanie

Endpoint `/optimization-control/` to **inteligentny harmonogram** urządzeń, który:
- ✅ Minimalizuje koszty (używa off-peak dla niskich priorytetów)
- ✅ Maksymalizuje użycie baterii (zużywa najpierw baterię)
- ✅ Szanuje priorytety (wysokie priorytety = ASAP)
- ✅ Zwraca szczegółowy harmonogram z wszystkimi informacjami

**Idealne do:** Automatyzacji zarządzania energią w domu/inteligentnym budynku! 🏠⚡

