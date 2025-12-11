# API Endpoints - Analysis Reporting Module

Dokumentacja endpointów dla modułu `analysis_reporting` w systemie IO.

**Base URL:** `http://localhost:6543/analysis-reporting/`

---

## 📋 Spis treści

1. [Report Criteria (Kryteria raportów)](#1-report-criteria-kryteria-raportów)
2. [Reports (Raporty)](#2-reports-raporty)
3. [Analyses (Analizy)](#3-analyses-analizy)
4. [Visualizations (Wizualizacje)](#4-visualizations-wizualizacje)
5. [Comparisons (Porównania raportów)](#5-comparisons-porównania-raportów)

---

## 1. Report Criteria (Kryteria raportów)

### 1.1. Tworzenie kryteriów raportu

```http
POST /analysis-reporting/criteria/
```

**Body:**
```json
{
  "location": "Lab",
  "device_type": "energy_meter",
  "date_from": "2025-10-01",
  "date_to": "2025-10-02",
  "date_created_from": "2025-10-01",
  "date_created_to": "2025-10-02"
}
```

**Response:**
```json
{
  "report_criteria_id": "uuid",
  "location": "Lab",
  "report_frequency": "MONTHLY",
  "device_type": "energy_meter",
  "date_created_from": "2025-10-01",
  "date_created_to": "2025-10-02"
}
```

### 1.2. Lista wszystkich kryteriów

```http
GET /analysis-reporting/criteria/
```

### 1.3. Pobieranie pojedynczych kryteriów

```http
GET /analysis-reporting/criteria/{id}/
```

### 1.4. Aktualizacja kryteriów

```http
PUT /analysis-reporting/criteria/{id}/
PATCH /analysis-reporting/criteria/{id}/
```

### 1.5. Usuwanie kryteriów

```http
DELETE /analysis-reporting/criteria/{id}/
```

---

## 2. Reports (Raporty)

### 2.1. Generowanie nowego raportu

```http
POST /analysis-reporting/reports/generate/
```

**Body:**
```json
{
  "criteria_id": "uuid",
  "generate_charts": true,
  "use_ai": false
}
```

**Parametry:**
- `criteria_id` (wymagany): UUID kryteriów raportu
- `generate_charts` (opcjonalny, domyślnie `false`): Czy generować wykresy
- `use_ai` (opcjonalny, domyślnie `false`): Czy używać AI do generowania opisów

**Response:**
```json
{
  "report_id": "uuid",
  "report_description": "Report for period 2025-10-01 - 2025-10-02",
  "report_criteria": {
    "report_criteria_id": "uuid",
    "location": "Lab",
    "device_type": "energy_meter"
  },
  "analyses": [
    {
      "analysis_id": "uuid",
      "analysis_type": "TRENDS",
      "analysis_summary": "{\"summary\": \"Analiza trendu na podstawie 48 pomiarów...\"}",
      "has_summary": true,
      "visualizations": []
    },
    {
      "analysis_id": "uuid",
      "analysis_type": "PEAK",
      "analysis_summary": "{\"summary\": \"Analiza szczytów obciążenia...\"}",
      "has_summary": true,
      "visualizations": []
    }
  ]
}
```

**Uwagi:**
- Automatycznie tworzy analizy **TRENDS** i **PEAK**
- Analiza **ANOMALY** musi być wygenerowana osobno (patrz 2.2)
- Jeśli `use_ai=true`, opisy są generowane przez AI (Groq API)
- Jeśli `use_ai=false`, używane są statyczne podsumowania

### 2.2. Generowanie analizy anomalii

```http
POST /analysis-reporting/reports/{id}/generate_anomaly/
```

**Body:**
```json
{
  "generate_chart": true,
  "use_ai": false
}
```

**Parametry:**
- `generate_chart` (opcjonalny, domyślnie `true`): Czy generować wykres
- `use_ai` (opcjonalny, domyślnie `false`): Czy używać AI do opisu

**Response:**
```json
{
  "analysis_id": "uuid",
  "analysis_type": "ANOMALY",
  "analysis_summary": "{\"summary\": \"Wykryto 0 anomalii w 48 pomiarach...\"}",
  "has_summary": true,
  "visualizations": [
    {
      "visualization_id": "uuid",
      "chart_type": "line_chart",
      "file_path": "/media/charts/anomaly_xyz.png"
    }
  ]
}
```

### 2.3. Lista wszystkich raportów

```http
GET /analysis-reporting/reports/
```

### 2.4. Pobieranie pojedynczego raportu

```http
GET /analysis-reporting/reports/{id}/
```

**Response:**
```json
{
  "report_id": "uuid",
  "report_description": "Report for period 2025-10-01 - 2025-10-02",
  "report_date": "2025-12-09T10:00:00Z",
  "report_criteria": {
    "report_criteria_id": "uuid",
    "location": "Lab",
    "device_type": "energy_meter",
    "date_created_from": "2025-10-01",
    "date_created_to": "2025-10-02"
  },
  "analyses": [
    {
      "analysis_id": "uuid",
      "analysis_type": "TRENDS",
      "analysis_summary": "{\"summary\": \"...\"}",
      "visualizations": []
    }
  ],
  "data_for_analysis": {
    "timestamps": ["2025-10-01T00:00:00Z", "2025-10-01T01:00:00Z"],
    "values": [5.2, 5.8]
  }
}
```

### 2.5. Eksport pełnego raportu

```http
GET /analysis-reporting/reports/{id}/export/
```

**Response:**
```json
{
  "report_id": "uuid",
  "report_description": "...",
  "analyses": [...],
  "data_for_analysis": {...}
}
```

### 2.6. Eksport tylko danych pomiarowych

```http
GET /analysis-reporting/reports/{id}/export_data/
```

**Response:**
```json
{
  "timestamps": ["2025-10-01T00:00:00Z", "2025-10-01T01:00:00Z"],
  "values": [5.2, 5.8]
}
```

### 2.7. Eksport raportu do PDF

```http
GET /analysis-reporting/reports/{id}/export_pdf/
```

**Response:**
- Plik PDF do pobrania
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="report_{id}.pdf"`

**PDF zawiera:**
- Nagłówek z tytułem i datą
- Informacje o raporcie (lokalizacja, urządzenie, okres)
- Statystyki (średnia, min, max, odchylenie standardowe)
- Szczegóły analiz (TRENDS, PEAK, ANOMALY)
- Wykresy (jeśli zostały wygenerowane)

### 2.8. Pobieranie raportów użytkownika

```http
GET /analysis-reporting/reports/by_user/?user_id=123
```

**Query Parameters:**
- `user_id` (wymagany): ID użytkownika

### 2.9. Aktualizacja raportu

```http
PUT /analysis-reporting/reports/{id}/
PATCH /analysis-reporting/reports/{id}/
```

### 2.10. Usuwanie raportu

```http
DELETE /analysis-reporting/reports/{id}/
```

---

## 3. Analyses (Analizy)

### 3.1. Lista wszystkich analiz

```http
GET /analysis-reporting/analyses/
```

### 3.2. Pobieranie pojedynczej analizy

```http
GET /analysis-reporting/analyses/{id}/
```

**Response:**
```json
{
  "analysis_id": "uuid",
  "analysis_type": "TRENDS",
  "analysis_summary": "{\"summary\": \"Analiza trendu...\", \"statistics\": {...}}",
  "has_summary": true,
  "analysis_date": "2025-12-09T10:00:00Z",
  "visualizations": [
    {
      "visualization_id": "uuid",
      "chart_type": "line_chart",
      "file_path": "/media/charts/trends_xyz.png"
    }
  ]
}
```

### 3.3. Aktualizacja analizy

```http
PUT /analysis-reporting/analyses/{id}/
PATCH /analysis-reporting/analyses/{id}/
```

### 3.4. Usuwanie analizy

```http
DELETE /analysis-reporting/analyses/{id}/
```

---

## 4. Visualizations (Wizualizacje)

### 4.1. Lista wszystkich wizualizacji

```http
GET /analysis-reporting/visualizations/
```

### 4.2. Pobieranie pojedynczej wizualizacji

```http
GET /analysis-reporting/visualizations/{id}/
```

**Response:**
```json
{
  "visualization_id": "uuid",
  "chart_type": "line_chart",
  "file_path": "/media/charts/trends_xyz.png",
  "created_at": "2025-12-09T10:00:00Z"
}
```

### 4.3. Aktualizacja wizualizacji

```http
PUT /analysis-reporting/visualizations/{id}/
PATCH /analysis-reporting/visualizations/{id}/
```

### 4.4. Usuwanie wizualizacji

```http
DELETE /analysis-reporting/visualizations/{id}/
```

---

## 5. Comparisons (Porównania raportów)

### 5.1. Tworzenie porównania

```http
POST /analysis-reporting/comparisons/compare/
```

**Body:**
```json
{
  "report_one_id": "uuid",
  "report_two_id": "uuid"
}
```

**Response:**
```json
{
  "compare_id": "uuid",
  "report_one": {
    "report_id": "uuid",
    "report_description": "Report for period 2025-10-01 - 2025-10-02"
  },
  "report_two": {
    "report_id": "uuid",
    "report_description": "Report for period 2025-11-01 - 2025-11-02"
  },
  "comparison_description": "{\"average_change\": 5.2, \"trend\": \"increase\", ...}",
  "visualization_file": "/media/comparisons/comparison_xyz.png",
  "compared_date": "2025-12-09T10:00:00Z"
}
```

**Porównanie zawiera:**
- Statystyki obu raportów (średnia, min, max)
- Zmianę procentową między okresami
- Wykres porównawczy (4 panele: linia, box plot, bar chart, statystyki)

### 5.2. Lista wszystkich porównań

```http
GET /analysis-reporting/comparisons/
```

### 5.3. Pobieranie pojedynczego porównania

```http
GET /analysis-reporting/comparisons/{id}/
```

### 5.4. Eksport porównania do PDF

```http
GET /analysis-reporting/comparisons/{id}/export_pdf/
```

**Response:**
- Plik PDF do pobrania
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="comparison_{id}.pdf"`

**PDF zawiera:**
- Metadane obu raportów
- Statystyki porównawcze
- Wykres porównawczy (4 panele)
- Wnioski ze zmian

### 5.5. Aktualizacja porównania

```http
PUT /analysis-reporting/comparisons/{id}/
PATCH /analysis-reporting/comparisons/{id}/
```

### 5.6. Usuwanie porównania

```http
DELETE /analysis-reporting/comparisons/{id}/
```

---

## 📝 Typy analiz

System obsługuje 3 typy analiz:

1. **TRENDS** (Analiza trendu)
   - Kierunek trendu (up/down/stable)
   - Zmiana procentowa
   - Regresja liniowa

2. **PEAK** (Analiza szczytów)
   - Maksymalne obciążenie
   - Liczba przekroczeń progu
   - Średnia wartość

3. **ANOMALY** (Analiza anomalii)
   - Detekcja metodą IQR (Interquartile Range)
   - Lista anomalii z timestampami
   - Statystyki (mean, std)

---

## 🎨 Wizualizacje

System generuje profesjonalne wykresy z użyciem **matplotlib** + **seaborn**:

- **TRENDS**: Wykres liniowy z gradientem i linią trendu
- **PEAK**: Wykres z zaznaczonymi szczytami i strefami
- **ANOMALY**: Wykres z podświetlonymi anomaliami i bounds
- **COMPARISON**: 4-panelowy wykres porównawczy

Kolory:
- TRENDS: `#2E86AB` → `#A23B72`
- PEAK: `#F18F01` → `#C73E1D`
- ANOMALY: `#4361EE` → `#D62828`

---

## 🤖 Generowanie opisów z AI

System może używać **Groq API** (model: `llama-3.3-70b-versatile`) do generowania opisów w języku polskim.

**Konfiguracja:**
- Klucz API: `GROQ_API_KEY` w `.env`
- Model: `llama-3.3-70b-versatile` (hardcoded w `analysis_reporting/config.py`)

**Walidacja AI:**
- Minimum 70% polskich znaków
- Regex sprawdzający podejrzane sekwencje
- Fallback na statyczne opisy w przypadku błędu

**Temperatury:**
- Analizy: `0.6`
- Raport: `0.5`

---

## 🔐 Uwagi

- Wszystkie endpointy są **bez autentykacji** (`authentication_classes = []`)
- Format daty: `YYYY-MM-DD`
- Format datetime: ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)
- Pliki przechowywane w `/media/charts/`, `/media/reports/`, `/media/comparisons/`

---

## 🚀 Przykładowy workflow

```bash
# 1. Utwórz kryteria
CRITERIA_ID=$(curl -s -X POST http://localhost:6543/analysis-reporting/criteria/ \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Lab",
    "device_type": "energy_meter",
    "date_from": "2025-10-01",
    "date_to": "2025-10-02",
    "date_created_from": "2025-10-01",
    "date_created_to": "2025-10-02"
  }' | jq -r '.report_criteria_id')

# 2. Wygeneruj raport (z wykresami, bez AI)
REPORT_ID=$(curl -s -X POST http://localhost:6543/analysis-reporting/reports/generate/ \
  -H "Content-Type: application/json" \
  -d "{
    \"criteria_id\": \"$CRITERIA_ID\",
    \"generate_charts\": true,
    \"use_ai\": false
  }" | jq -r '.report_id')

# 3. Dodaj analizę anomalii (z AI)
curl -s -X POST http://localhost:6543/analysis-reporting/reports/$REPORT_ID/generate_anomaly/ \
  -H "Content-Type: application/json" \
  -d '{
    "generate_chart": true,
    "use_ai": true
  }'

# 4. Pobierz raport jako PDF
curl -s http://localhost:6543/analysis-reporting/reports/$REPORT_ID/export_pdf/ \
  --output report.pdf

# 5. Otwórz PDF
open report.pdf
```

---

## 📦 Modele danych

### ReportCriteria
```python
{
  "report_criteria_id": UUID,
  "location": CharField,
  "report_frequency": CharField (DAILY/WEEKLY/MONTHLY),
  "date_created_from": DateField,
  "date_created_to": DateField,
  "device_type": CharField
}
```

### Report
```python
{
  "report_id": UUID,
  "report_description": TextField,
  "report_date": DateTimeField,
  "report_criteria": ForeignKey(ReportCriteria),
  "data_for_analysis": JSONField,
  "created_by_id": IntegerField (nullable)
}
```

### Analysis
```python
{
  "analysis_id": UUID,
  "analysis_type": CharField (TRENDS/PEAK/ANOMALY),
  "analysis_summary": JSONField,
  "analysis_date": DateTimeField,
  "report": ForeignKey(Report)
}
```

### Visualization
```python
{
  "visualization_id": UUID,
  "chart_type": CharField,
  "file_path": CharField,
  "created_at": DateTimeField,
  "analysis": ForeignKey(Analysis)
}
```

### ReportCompare
```python
{
  "compare_id": UUID,
  "report_one": ForeignKey(Report),
  "report_two": ForeignKey(Report),
  "comparison_description": JSONField,
  "visualization_file": CharField,
  "compared_date": DateTimeField
}
```

---

**Wersja:** 1.0  
**Data:** 9 grudnia 2025  
**Autor:** System IO - Analysis Reporting Module
