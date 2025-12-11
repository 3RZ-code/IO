"""
Utilities dla obliczeń analitycznych w module analysis_reporting
Zawiera funkcje do analizy danych z sensorów
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Sum, Count, Q
import statistics


class AnalysisUtils:
    """
    Klasa pomocnicza dla obliczeń analitycznych
    """
    
    @staticmethod
    def calculate_cost_analysis(readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Oblicza analizę kosztów na podstawie odczytów energii
        
        Args:
            readings: Lista odczytów z sensorów (power_kw)
        
        Returns:
            Słownik z analizą kosztów
        """
        energy_readings = [
            r for r in readings 
            if r.get('metric') == 'power_kw'
        ]
        
        if not energy_readings:
            return {
                "total_consumption_kwh": 0,
                "average_power_kw": 0,
                "peak_power_kw": 0,
                "estimated_cost": 0,
                "cost_per_location": {}
            }
        
        # Obliczenia
        values = [r['value'] for r in energy_readings]
        total_kwh = sum(values)
        avg_power = statistics.mean(values)
        peak_power = max(values)
        
        # Zakładamy cenę za kWh (przykładowo 0.15 EUR/kWh)
        cost_per_kwh = 0.15
        estimated_cost = total_kwh * cost_per_kwh
        
        # Analiza per lokalizacja
        locations = {}
        for reading in energy_readings:
            loc = reading.get('location', 'Unknown')
            if loc not in locations:
                locations[loc] = []
            locations[loc].append(reading['value'])
        
        cost_per_location = {
            loc: {
                "consumption_kwh": sum(vals),
                "avg_power_kw": statistics.mean(vals),
                "cost": sum(vals) * cost_per_kwh
            }
            for loc, vals in locations.items()
        }
        
        return {
            "total_consumption_kwh": round(total_kwh, 2),
            "average_power_kw": round(avg_power, 2),
            "peak_power_kw": round(peak_power, 2),
            "estimated_cost": round(estimated_cost, 2),
            "cost_per_location": cost_per_location,
            "readings_count": len(energy_readings)
        }
    
    @staticmethod
    def calculate_peak_load(readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analizuje szczytowe obciążenia
        
        Args:
            readings: Lista odczytów z sensorów
        
        Returns:
            Słownik z analizą szczytów
        """
        if not readings:
            return {
                "peak_value": 0,
                "peak_timestamp": None,
                "peak_location": None,
                "peak_device": None,
                "average_value": 0
            }
        
        # Znajdź szczyt
        peak_reading = max(readings, key=lambda x: x.get('value', 0))
        
        # Oblicz średnią
        values = [r['value'] for r in readings]
        avg_value = statistics.mean(values)
        
        # Znajdź wszystkie szczyty (wartości > 90% max)
        threshold = peak_reading['value'] * 0.9
        peak_events = [
            r for r in readings 
            if r['value'] >= threshold
        ]
        
        return {
            "peak_value": peak_reading['value'],
            "peak_timestamp": peak_reading.get('timestamp'),
            "peak_location": peak_reading.get('location'),
            "peak_device": peak_reading.get('device_id'),
            "peak_metric": peak_reading.get('metric'),
            "average_value": round(avg_value, 2),
            "peak_events_count": len(peak_events),
            "peak_threshold": round(threshold, 2)
        }
    
    @staticmethod
    def detect_anomalies(readings: List[Dict[str, Any]], 
                        threshold_std: float = 3.0) -> Dict[str, Any]:
        """
        Wykrywa anomalie w danych używając metody odchylenia standardowego
        
        Args:
            readings: Lista odczytów z sensorów
            threshold_std: Próg wykrywania (ilość odchyleń standardowych)
        
        Returns:
            Słownik z wykrytymi anomaliami
        """
        if len(readings) < 3:
            return {
                "anomalies_detected": False,
                "anomalies": [],
                "anomaly_count": 0
            }
        
        values = [r['value'] for r in readings]
        mean_value = statistics.mean(values)
        
        try:
            std_dev = statistics.stdev(values)
        except statistics.StatisticsError:
            std_dev = 0
        
        if std_dev == 0:
            return {
                "anomalies_detected": False,
                "anomalies": [],
                "anomaly_count": 0,
                "reason": "No variation in data"
            }
        
        # Wykryj anomalie
        anomalies = []
        lower_bound = mean_value - (threshold_std * std_dev)
        upper_bound = mean_value + (threshold_std * std_dev)
        
        for idx, reading in enumerate(readings):
            value = reading['value']
            if value < lower_bound or value > upper_bound:
                anomalies.append({
                    "index": idx,
                    "reading_id": reading.get('id'),
                    "timestamp": reading.get('timestamp'),
                    "location": reading.get('location'),
                    "device_id": reading.get('device_id'),
                    "metric": reading.get('metric'),
                    "value": value,
                    "deviation": abs(value - mean_value) / std_dev,
                    "type": "high" if value > upper_bound else "low"
                })
        
        return {
            "anomalies_detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "statistics": {
                "mean": round(mean_value, 2),
                "std_dev": round(std_dev, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2)
            }
        }
    
    @staticmethod
    def calculate_trends(readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Oblicza trendy w danych czasowych
        
        Args:
            readings: Lista odczytów z sensorów (muszą być posortowane chronologicznie)
        
        Returns:
            Słownik z analizą trendów
        """
        if len(readings) < 2:
            return {
                "trend": "insufficient_data",
                "trend_direction": None,
                "change_percentage": 0
            }
        
        # Sortuj chronologicznie
        sorted_readings = sorted(readings, key=lambda x: x.get('timestamp', ''))
        
        values = [r['value'] for r in sorted_readings]
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        change = avg_second - avg_first
        change_percentage = (change / avg_first * 100) if avg_first != 0 else 0
        
        # Określ trend
        if abs(change_percentage) < 5:
            trend = "stable"
        elif change_percentage > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "trend_direction": "up" if change > 0 else "down" if change < 0 else "stable",
            "change_percentage": round(change_percentage, 2),
            "first_period_avg": round(avg_first, 2),
            "second_period_avg": round(avg_second, 2),
            "absolute_change": round(change, 2)
        }
    
    @staticmethod
    def aggregate_by_time_period(readings: List[Dict[str, Any]], 
                                 period: str = 'daily') -> Dict[str, Any]:
        """
        Agreguje dane według okresów czasowych
        
        Args:
            readings: Lista odczytów
            period: 'hourly', 'daily', 'weekly', 'monthly'
        
        Returns:
            Słownik z zagregowanymi danymi
        """
        from collections import defaultdict
        
        aggregated = defaultdict(list)
        
        for reading in readings:
            timestamp = reading.get('timestamp')
            if not timestamp:
                continue
            
            # Parsuj timestamp jeśli to string
            if isinstance(timestamp, str):
                try:
                    from django.utils.dateparse import parse_datetime
                    timestamp = parse_datetime(timestamp)
                except:
                    continue
            
            # Określ klucz agregacji
            if period == 'hourly':
                key = timestamp.strftime('%Y-%m-%d %H:00')
            elif period == 'daily':
                key = timestamp.strftime('%Y-%m-%d')
            elif period == 'weekly':
                key = timestamp.strftime('%Y-W%W')
            elif period == 'monthly':
                key = timestamp.strftime('%Y-%m')
            else:
                key = timestamp.strftime('%Y-%m-%d')
            
            aggregated[key].append(reading['value'])
        
        # Oblicz statystyki dla każdego okresu
        result = {}
        for period_key, values in aggregated.items():
            result[period_key] = {
                "count": len(values),
                "sum": round(sum(values), 2),
                "average": round(statistics.mean(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2)
            }
        
        return result
    
    @staticmethod
    def compare_periods(period_one_readings: List[Dict[str, Any]], 
                       period_two_readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Porównuje dane z dwóch okresów (listy readings)
        
        Args:
            period_one_readings: Lista odczytów z pierwszego okresu
            period_two_readings: Lista odczytów z drugiego okresu
        
        Returns:
            Słownik z porównaniem statystyk
        """
        # Wyciągnij wartości z obu okresów
        values_one = [r['value'] for r in period_one_readings if 'value' in r and r['value'] is not None]
        values_two = [r['value'] for r in period_two_readings if 'value' in r and r['value'] is not None]
        
        if not values_one or not values_two:
            return {
                "error": "Insufficient data for comparison",
                "period1_count": len(values_one),
                "period2_count": len(values_two)
            }
        
        # Oblicz statystyki dla obu okresów
        period1_avg = statistics.mean(values_one)
        period2_avg = statistics.mean(values_two)
        period1_median = statistics.median(values_one)
        period2_median = statistics.median(values_two)
        period1_max = max(values_one)
        period2_max = max(values_two)
        period1_min = min(values_one)
        period2_min = min(values_two)
        
        # Oblicz różnice
        avg_difference = period2_avg - period1_avg
        percentage_change = (avg_difference / period1_avg * 100) if period1_avg != 0 else 0
        
        # Określ trend
        if percentage_change > 5:
            trend = "increasing"
        elif percentage_change < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "period1_avg": round(period1_avg, 2),
            "period2_avg": round(period2_avg, 2),
            "period1_median": round(period1_median, 2),
            "period2_median": round(period2_median, 2),
            "period1_max": round(period1_max, 2),
            "period2_max": round(period2_max, 2),
            "period1_min": round(period1_min, 2),
            "period2_min": round(period2_min, 2),
            "difference": round(avg_difference, 2),
            "percentage_change": round(percentage_change, 2),
            "trend": trend,
            "period1_count": len(values_one),
            "period2_count": len(values_two)
        }
