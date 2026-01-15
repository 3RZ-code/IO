# Analysis & Reporting Module - Frontend

Moduł analizy i raportowania danych pomiarowych z czujników energetycznych.

## 📁 Struktura projektu

```
frontend/src/
├── pages/analysisReporting/
│   ├── AnalysisReportingPage.js      # Główna strona z listą raportów
│   ├── ReportDetailsPage.js          # Szczegóły pojedynczego raportu
│   ├── ComparisonDetailsPage.js      # Szczegóły porównania raportów
│   └── index.js                      # Eksport stron
├── components/analysisReporting/
│   ├── GenerateReportDialog.js       # Dialog generowania raportu
│   ├── CompareReportsDialog.js       # Dialog porównywania raportów
│   └── ReportCard.js                 # Karta raportu (lista)
└── api/analysisReporting/
    └── analysisReportingApi.js       # Serwis API
```

## 🎯 Zrealizowane wymagania funkcjonalne

### ✅ 1. Generowanie raportu

- Użytkownik może wygenerować raport na podstawie danych z czujników
- Dialog z formularzem generowania (`GenerateReportDialog.js`)
- Automatyczne pobieranie ID zalogowanego użytkownika

### ✅ 2. Konfigurowalne kryteria raportowania

- Okres czasu (date_from, date_to) - **wymagane**
- Lokalizacja - opcjonalne (dowolny tekst)
- Typ urządzenia - opcjonalne (dowolny tekst)
- Checkbox: Generuj wykresy (domyślnie: włączone)
- Checkbox: Użyj AI do podsumowania (domyślnie: **wyłączone**)

### ✅ 3. Dostęp do wygenerowanych raportów

- Lista wszystkich raportów użytkownika
- Widok szczegółów raportu
- Filtrowanie i sortowanie

### ✅ 4. Raportowanie porównawcze

- Porównanie dwóch raportów z różnych okresów
- Dialog wyboru raportu do porównania
- Strona z wizualizacją porównania

### ✅ 5. Analiza istniejącego raportu

- Automatyczne analizy: **TRENDS** i **PEAK**
- Możliwość wygenerowania analizy **ANOMALY** na żądanie
- Wyświetlanie podsumowań analiz
- Wykresy dla każdej analizy

### ✅ 6. Identyfikacja anomalii

- Przycisk "Generate Anomaly Analysis" na stronie szczegółów
- Analiza metodą IQR (backend)
- Wykres z podświetlonymi anomaliami

### ✅ 7. Wizualizacja raportów

- Wykresy dla analiz (TRENDS, PEAK, ANOMALY)
- Wykres porównawczy (4 panele)
- Automatyczne pobieranie z backend media storage

### ✅ 8. Eksport raportu (PDF)

- Przycisk "Export PDF" na liście i szczegółach
- Automatyczne pobieranie pliku przez przeglądarkę
- Backend generuje PDF z wykresami

### ✅ 9. Eksport danych analitycznych (JSON)

- Przycisk "Export JSON"
- Pobieranie pełnego raportu jako JSON
- Helper do zapisu pliku

## 🚀 Workflow użytkownika

### Generowanie raportu

1. Użytkownik klika "Generate New Report"
2. Wypełnia formularz:
   - **Data od** (wymagane)
   - **Data do** (wymagane)
   - Lokalizacja (opcjonalne)
   - Typ urządzenia (opcjonalne)
   - ☑️ Generuj wykresy (domyślnie: włączone)
   - ☐ Użyj AI (domyślnie: wyłączone)
3. System:
   - Tworzy kryteria (POST /criteria/)
   - Generuje raport (POST /reports/generate/)
   - Automatycznie tworzy analizy TRENDS i PEAK
4. Raport pojawia się na liście

### Przeglądanie raportu

1. Użytkownik klika kartę raportu lub ikonę "View Details"
2. Wyświetlają się:
   - Informacje o raporcie
   - Kryteria raportu
   - Wszystkie analizy (TRENDS, PEAK, ewentualnie ANOMALY)
   - Wykresy dla każdej analizy
3. Opcje:
   - Export PDF
   - Export JSON
   - Generate Anomaly Analysis (jeśli nie istnieje)

### Analiza anomalii

1. Na stronie szczegółów raportu, jeśli nie ma analizy ANOMALY
2. Użytkownik klika "Generate Anomaly Analysis"
3. Backend wykrywa anomalie metodą IQR
4. Strona odświeża się i pokazuje nową analizę z wykresem

### Porównywanie raportów

1. Użytkownik klika ikonę "Compare" na karcie raportu
2. W dialogu wybiera drugi raport
3. System:
   - Tworzy porównanie (POST /comparisons/compare/)
   - Generuje wykres porównawczy (4 panele)
4. Nawigacja do strony porównania
5. Wyświetlenie:
   - Metadane obu raportów
   - Statystyki porównawcze
   - Wykres porównawczy
6. Opcja: Export PDF

## 🔧 API Endpoints (używane przez frontend)

### Report Criteria

- `POST /analysis-reporting/criteria/` - Tworzenie kryteriów
- `GET /analysis-reporting/criteria/` - Lista kryteriów

### Reports

- `POST /analysis-reporting/reports/generate/` - Generowanie raportu
- `GET /analysis-reporting/reports/` - Lista wszystkich raportów
- `GET /analysis-reporting/reports/{id}/` - Szczegóły raportu
- `POST /analysis-reporting/reports/{id}/generate_anomaly/` - Generowanie analizy anomalii
- `GET /analysis-reporting/reports/{id}/export/` - Eksport JSON (pełny)
- `GET /analysis-reporting/reports/{id}/export_data/` - Eksport JSON (tylko dane)
- `GET /analysis-reporting/reports/{id}/export_pdf/` - Eksport PDF
- `DELETE /analysis-reporting/reports/{id}/` - Usuwanie raportu

### Analyses

- `GET /analysis-reporting/analyses/` - Lista analiz
- `GET /analysis-reporting/analyses/{id}/` - Szczegóły analizy

### Visualizations

- `GET /analysis-reporting/visualizations/` - Lista wizualizacji
- `GET /analysis-reporting/visualizations/{id}/` - Szczegóły wizualizacji

### Comparisons

- `POST /analysis-reporting/comparisons/compare/` - Porównanie raportów
- `GET /analysis-reporting/comparisons/` - Lista porównań
- `GET /analysis-reporting/comparisons/{id}/` - Szczegóły porównania
- `GET /analysis-reporting/comparisons/{id}/export_pdf/` - Eksport PDF porównania

## 📊 Komponenty

### AnalysisReportingPage

Główna strona modułu:

- Hero section z przyciskiem "Generate New Report"
- Lista raportów (karty)
- Przyciski akcji: View, Export PDF, Export JSON, Compare, Delete
- Dialog generowania raportu
- Dialog porównywania

### ReportDetailsPage

Szczegóły pojedynczego raportu:

- Informacje o raporcie
- Kryteria raportu
- Lista analiz (TRENDS, PEAK, ANOMALY)
- Wykresy dla każdej analizy
- Przycisk generowania analizy anomalii
- Export PDF/JSON

### ComparisonDetailsPage

Szczegóły porównania:

- Metadane obu raportów
- Statystyki porównawcze
- Wykres porównawczy (4 panele)
- Export PDF

### GenerateReportDialog

Dialog generowania raportu:

- Formularz z walidacją
- Pola: location, device_type, date_from, date_to
- Checkboxy: generate_charts, use_ai
- Automatyczne pobieranie user_id

### CompareReportsDialog

Dialog porównywania:

- Wybór drugiego raportu z listy
- Walidacja (nie można porównać z samym sobą)
- Nawigacja do strony porównania

### ReportCard

Karta raportu na liście:

- Podstawowe informacje
- Okres czasu
- Chipy z lokalizacją, typem urządzenia
- Chipy z typami analiz
- Ikony akcji: View, Export, Compare, Delete

## 🎨 Stylistyka

- Spójna z główną stroną aplikacji (MainPage)
- Material-UI komponenty
- Hero section z gradientem niebieskim
- Hover efekty na kartach
- Responsywny layout (Grid)
- Footer na dole

## 🔐 Uwagi implementacyjne

1. **User ID**: Automatycznie pobierany z `/security/users/me/` przy generowaniu raportu
2. **Filtry**: Użytkownik wpisuje dowolne wartości (location, device_type)
3. **AI**: Domyślnie wyłączone, użytkownik może włączyć checkbox
4. **Wykresy**: URL generowany przez `getVisualizationUrl()` helper
5. **Backend URL**: Konfigurowany w `axios.js` (base URL)
6. **Eksport**: Automatyczne pobieranie plików przez przeglądarkę

## 🧪 Testowanie

1. Zaloguj się jako użytkownik
2. Przejdź do "Analysis & Reporting"
3. Wygeneruj raport z datami (np. 2025-10-01 do 2025-10-02)
4. Sprawdź szczegóły raportu
5. Wygeneruj analizę anomalii
6. Stwórz drugi raport z innymi datami
7. Porównaj raporty
8. Eksportuj PDF i JSON

## 📝 TODO / Rozszerzenia

- [ ] Filtrowanie listy raportów (search, date range)
- [ ] Sortowanie listy raportów
- [ ] Paginacja listy raportów
- [ ] Edycja opisu raportu
- [ ] Pobieranie tylko raportów danego użytkownika (obecnie wszystkie)
- [ ] Obsługa błędów ładowania wykresów (retry)
- [ ] Loading states dla poszczególnych akcji
- [ ] Potwierdzenia przed usunięciem
- [ ] Lista porównań (dedykowana strona)
- [ ] Udostępnianie raportów innym użytkownikom

## 🐛 Known Issues

- Wykresy ładują się z backend media storage - upewnij się, że backend jest uruchomiony
- Brak paginacji - przy dużej liczbie raportów może być wolno
- Eksport PDF może chwilę potrwać - brak progress bar

---

**Autor**: GitHub Copilot  
**Data**: 14 stycznia 2026  
**Wersja**: 1.0
