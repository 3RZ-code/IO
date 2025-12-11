# Optimization Control - Dokumentacja Endpointu

## 📍 Endpoint

**URL:** `POST /optimization-control/`

## 🎯 Cel

Endpoint generuje **optymalny harmonogram włączania urządzeń** z obliczaniem oszczędności na podstawie:
- Priorytetów urządzeń (z `data_acquisition.Device`)
- Dostępności baterii (z `simulation.BatteryState`)
- **Taryf energetycznych z harmonogramem tygodniowym:**
  - Taryfa dzienna: **0.6212 zł/kWh**
  - Taryfa nocna: **0.6036 zł/kWh**
  - Pon-Pt: 22:00-06:00 i 13:00-15:00 = nocna, reszta = dzienna
  - Weekend: cały dzień = nocna
- Produkcji energii z modułu `simulation.GenerationHistory`
- Oblicza **oszczędności** przy optymalizacji harmonogramu

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
  "tariffs": {
    "day_price_pln_per_kwh": 0.6212,
    "night_price_pln_per_kwh": 0.6036,
    "schedule": {
      "weekday": "22:00-06:00 i 13:00-15:00 = nocna, reszta = dzienna",
      "weekend": "cały dzień = nocna"
    }
  },
  "summary": {
    "devices_count": 5,
    "total_demand_kwh": 12.5,
    "generation_kwh": 45.2,
    "battery_start_kwh": 50.0,
    "battery_used_kwh": 12.5,
    "battery_remaining_kwh": 37.5
  },
  "costs": {
    "optimal_total_pln": 7.5234,
    "reference_total_pln": 7.7650,
    "savings_pln": 0.2416,
    "savings_percent": 3.11
  },
  "energy_distribution": {
    "optimal": {
      "night_kwh": 8.5,
      "day_kwh": 4.0
    },
    "reference": {
      "night_kwh": 3.2,
      "day_kwh": 9.3
    },
    "shift_to_night_kwh": 5.3
  },
  "optimal_schedule": [
    {
      "device_id": 1,
      "device_name": "Klimatyzacja",
      "priority": 0,
      "power_kw": 2.5,
      "start": "2025-12-12T06:00:00+01:00",
      "end": "2025-12-12T07:00:00+01:00",
      "tariff": "day",
      "energy_kwh": 2.5,
      "battery_used_kwh": 2.5,
      "grid_energy_kwh": 0.0,
      "cost_pln": 0.0
    },
    {
      "device_id": 2,
      "device_name": "Pralka",
      "priority": 2,
      "power_kw": 1.0,
      "start": "2025-12-12T22:00:00+01:00",
      "end": "2025-12-12T23:00:00+01:00",
      "tariff": "night",
      "energy_kwh": 1.0,
      "battery_used_kwh": 0.0,
      "grid_energy_kwh": 1.0,
      "cost_pln": 0.6036
    }
  ],
  "reference_schedule": [
    {
      "device_id": 1,
      "device_name": "Klimatyzacja",
      "priority": 0,
      "power_kw": 2.5,
      "start": "2025-12-12T00:00:00+01:00",
      "end": "2025-12-12T01:00:00+01:00",
      "tariff": "night",
      "energy_kwh": 2.5,
      "battery_used_kwh": 2.5,
      "grid_energy_kwh": 0.0,
      "cost_pln": 0.0
    }
  ]
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

**Taryfa Nocna (tańsza):** 0.6036 zł/kWh
- **Poniedziałek-Piątek:**
  - 22:00 - 06:00 (noc)
  - 13:00 - 15:00 (południe)
- **Weekend (sobota-niedziela):**
  - Cały dzień (24h)

**Taryfa Dzienna (droższa):** 0.6212 zł/kWh
- **Poniedziałek-Piątek:**
  - 06:00 - 13:00
  - 15:00 - 22:00

### Krok 3: Sortowanie Urządzeń

Urządzenia są sortowane **rosnąco po priorytecie**:
- Priorytet 0 (najwyższy) → uruchamiane najpierw
- Priorytet 1 → następne
- Priorytet 2 (najniższy) → na końcu

### Krok 4: Harmonogramowanie

Endpoint generuje **DWA harmonogramy**:

#### A) Harmonogram Optymalny
Dla każdego urządzenia:
1. **Wybór slotu czasowego:**
   - Jeśli `priority >= 2` → próbuje umieścić w **taryfie nocnej** (jeśli dostępne)
   - Jeśli `priority < 2` → umieszcza w **taryfie dziennej** (ASAP)
   - Jeśli brak slotów dziennych → używa nocnych
   - Jeśli brak wszystkich slotów → używa ostatniego dostępnego

2. **Użycie baterii:**
   - Najpierw zużywa energię z baterii
   - Jeśli bateria się wyczerpie → przechodzi na sieć
   - `battery_used_kwh` = min(pozostała bateria, zapotrzebowanie urządzenia)

3. **Obliczanie kosztów:**
   - `grid_energy_kwh` = zapotrzebowanie - energia z baterii
   - `cost_pln` = grid_energy_kwh × cena_taryfy

#### B) Harmonogram Referencyjny (bez optymalizacji)
- Wszystkie urządzenia uruchamiane **ASAP** (kolejno)
- Bez przesuwania do tańszych taryf
- Używany do porównania i obliczenia oszczędności

### Krok 5: Obliczenia Oszczędności

- **optimal_total_pln** - Koszt w harmonogramie optymalnym
- **reference_total_pln** - Koszt w harmonogramie referencyjnym
- **savings_pln** - Oszczędności w złotych (reference - optimal)
- **savings_percent** - Oszczędności w procentach
- **shift_to_night_kwh** - Ile kWh zostało przesunięte do taryfy nocnej

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

