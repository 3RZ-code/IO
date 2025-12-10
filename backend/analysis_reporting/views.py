"""
Views dla modułu analysis_reporting
Zawiera ViewSety REST API oraz ReportManager z logiką biznesową
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Report, ReportCriteria, Analysis, Visualization, ReportCompare
from .serializers import (
    ReportSerializer, 
    ReportCriteriaSerializer, 
    AnalysisSerializer, 
    VisualizationSerializer,
    ReportCompareSerializer
)
from data_acquisition.models import DeviceReading
from .utils.analysis_utils import AnalysisUtils
from .utils.ai_generator import AIGenerator


def index(request):
    return HttpResponse("Analysis & Reporting Module")


# ============================================================================
#                           REPORT MANAGER
# ============================================================================

class ReportManager:
    """
    Manager zarządzający operacjami na raportach.
    Implementuje logikę biznesową modułu analysis_reporting.
    """
    
    # ========== CRUD Operations ==========
    
    @staticmethod
    def save_report(report: Report) -> Report:
        """
        Zapisuje raport do bazy danych
        Args:
            report: Obiekt Report do zapisania
        Returns:
            Zapisany obiekt Report
        """
        report.save()
        return report
    
    @staticmethod
    def find_report_by_id(report_id: str) -> Optional[Report]:
        """
        Znajduje raport po ID
        Args:
            report_id: UUID raportu
        Returns:
            Obiekt Report lub None
        """
        try:
            return Report.objects.prefetch_related(
                'analyses__visualizations',
                'report_criteria'
            ).get(report_id=report_id)
        except Report.DoesNotExist:
            return None
    
    @staticmethod
    def find_report_by_user_id(user_id: int) -> List[Report]:
        """
        Znajduje wszystkie raporty utworzone przez użytkownika
        Args:
            user_id: ID użytkownika
        Returns:
            Lista raportów
        """
        return list(Report.objects.filter(
            created_by_id=user_id
        ).prefetch_related(
            'analyses__visualizations',
            'report_criteria'
        ).order_by('-created_timestamp'))
    
    @staticmethod
    def find_all_reports() -> List[Report]:
        """
        Zwraca wszystkie raporty
        Returns:
            Lista wszystkich raportów
        """
        return list(Report.objects.prefetch_related(
            'analyses__visualizations',
            'report_criteria'
        ).all())
    
    @staticmethod
    def delete_report_id(report_id: str) -> bool:
        """
        Usuwa raport po ID
        Args:
            report_id: UUID raportu
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        try:
            report = Report.objects.get(report_id=report_id)
            report.delete()
            return True
        except Report.DoesNotExist:
            return False
    
    @staticmethod
    def find_report_by_criteria(criteria: ReportCriteria) -> List[Report]:
        """
        Znajduje raporty spełniające określone kryteria
        Args:
            criteria: Obiekt ReportCriteria
        Returns:
            Lista raportów pasujących do kryteriów
        """
        return list(Report.objects.filter(
            report_criteria=criteria
        ).prefetch_related(
            'analyses__visualizations'
        ))
    
    # ========== Report Generation ==========
    
    @staticmethod
    def generate_report(report_criteria: ReportCriteria, generate_charts: bool = False, use_ai: bool = False) -> Report:
        """
        Generuje raport na podstawie kryteriów
        
        Args:
            report_criteria: Kryteria raportu (okres czasu, lokalizacja, typ urządzenia)
            generate_charts: Czy generować wykresy dla analiz
            use_ai: Czy używać AI do generowania opisów (wymaga klucza API Groq)
        
        Returns:
            Wygenerowany obiekt Report z analizami TRENDS i PEAK
        
        Raises:
            ValueError: Jeśli kryteria są niepełne lub nieprawidłowe
        
        Process:
            1. Waliduje kryteria (daty wymagane)
            2. Pobiera dane z data_acquisition na podstawie kryteriów
            3. Tworzy raport z danymi
            4. Automatycznie tworzy analizy: TRENDS i PEAK z realnymi obliczeniami
            5. Opcjonalnie generuje wykresy
            6. Jeśli use_ai=True, generuje opisy AI dla raportu i analiz
        """
        # Walidacja kryteriów
        if not report_criteria.validate_type():
            raise ValueError("Kryteria raportu są niepełne. Wymagane są daty rozpoczęcia i zakończenia.")
        
        if not report_criteria.date_created_from or not report_criteria.date_created_to:
            raise ValueError("Daty rozpoczęcia i zakończenia są wymagane do wygenerowania raportu.")
        
        # Pobierz dane z modułu data_acquisition
        sensor_data = ReportManager._fetch_sensor_data(report_criteria)
        
        # Sprawdź czy są dane
        if sensor_data['count'] == 0:
            raise ValueError("Brak danych dla podanych kryteriów. Nie można wygenerować raportu.")
        
        # Tworzenie raportu z domyślnym opisem
        report = Report.objects.create(
            report_criteria=report_criteria,
            data_for_analysis=sensor_data,
            report_description=f"Report for period {report_criteria.date_created_from} - {report_criteria.date_created_to}"
        )
        print(f"✓ Report created: {report.report_id}")
        
        # Automatycznie generuj analizy TRENDS i PEAK z realnymi obliczeniami
        print(f"Calling _generate_automatic_analyses...")
        ReportManager._generate_automatic_analyses(report, sensor_data, generate_charts, use_ai)
        print(f"✓ Analyses generated")
        
        # Generuj AI opis raportu TYLKO jeśli use_ai=True
        if use_ai:
            ai_report_desc = AIGenerator.generate_report_description(
                criteria={
                    'location': report_criteria.location,
                    'device_type': report_criteria.device_type,
                    'date_from': str(report_criteria.date_created_from),
                    'date_to': str(report_criteria.date_created_to)
                },
                analyses_summaries=[
                    {
                        'type': analysis.analysis_type,
                        'key_findings': analysis.analysis_title
                    }
                    for analysis in report.analyses.all()
                ],
                readings_count=sensor_data['count']
            )
            
            # Zaktualizuj opis jeśli AI wygenerował
            if ai_report_desc:
                report.report_description = ai_report_desc
                report.save()
        
        return report
    
    @staticmethod
    def _fetch_sensor_data(criteria: ReportCriteria) -> Dict[str, Any]:
        """
        Pobiera dane z sensorów z modułu data_acquisition
        Używa Django ORM do bezpośredniego dostępu do DeviceReading
        
        Args:
            criteria: Kryteria filtrowania
        
        Returns:
            Słownik z danymi sensorów
        """
        # Buduj query na podstawie kryteriów
        queryset = DeviceReading.objects.select_related('device').all()
        
        if criteria.location:
            queryset = queryset.filter(location=criteria.location)
        if criteria.device_type:
            queryset = queryset.filter(device_type=criteria.device_type)
        if criteria.date_created_from:
            queryset = queryset.filter(timestamp__date__gte=criteria.date_created_from)
        if criteria.date_created_to:
            queryset = queryset.filter(timestamp__date__lte=criteria.date_created_to)
        
        # Zbierz dane
        readings_qs = queryset.values(
            'id', 'timestamp', 'device_id', 'device_type', 
            'location', 'metric', 'value', 'unit', 
            'signal_dbm', 'status'
        )
        
        # Konwertuj datetime do string dla JSON serializacji
        readings = []
        for reading in readings_qs:
            reading_dict = dict(reading)
            if 'timestamp' in reading_dict and reading_dict['timestamp']:
                reading_dict['timestamp'] = reading_dict['timestamp'].isoformat()
            readings.append(reading_dict)
        
        return {
            "readings": readings,
            "count": len(readings),
            "criteria": {
                "location": criteria.location,
                "device_type": criteria.device_type,
                "date_from": str(criteria.date_created_from) if criteria.date_created_from else None,
                "date_to": str(criteria.date_created_to) if criteria.date_created_to else None,
            },
            "fetched_at": timezone.now().isoformat()
        }
    
    @staticmethod
    def _generate_automatic_analyses(report: Report, sensor_data: Dict[str, Any], generate_charts: bool = False, use_ai: bool = False) -> None:
        """
        Generuje automatyczne analizy dla raportu (tylko TRENDS i PEAK) z realnymi obliczeniami
        Analiza ANOMALY tworzona jest osobno na żądanie użytkownika
        
        Args:
            report: Raport do którego dodajemy analizy
            sensor_data: Dane z sensorów
            generate_charts: Czy generować wykresy
            use_ai: Czy używać AI do generowania opisów
        """
        print(f"=== STARTING _generate_automatic_analyses ===")
        readings = sensor_data.get('readings', [])
        print(f"Readings count: {len(readings)}")
        
        if not readings:
            print("No readings, returning")
            return
        
        # === ANALIZA TRENDÓW ===
        print("Calculating trends...")
        trends_result = AnalysisUtils.calculate_trends(readings)
        print(f"Trends result: {trends_result}")
        
        # Generuj opis dla analysis_summary - AI lub statyczny
        if use_ai:
            ai_description = AIGenerator.generate_analysis_description(
                'TRENDS',
                trends_result,
                len(readings)
            )
            if ai_description:
                print(f"✓ TRENDS AI: {len(ai_description)} chars: {ai_description[:100]}")
                trends_result['summary'] = ai_description
            else:
                print("✗ TRENDS AI: brak opisu - używam statycznego")
                trends_result['summary'] = f"Analiza trendu na podstawie {len(readings)} pomiarów. Kierunek trendu: {trends_result.get('trend_direction', 'N/A')}, zmiana: {trends_result.get('change_percentage', 0):.2f}%."
        else:
            print("ℹ TRENDS: używam statycznego podsumowania")
            trends_result['summary'] = f"Analiza trendu na podstawie {len(readings)} pomiarów. Kierunek trendu: {trends_result.get('trend_direction', 'N/A')}, zmiana: {trends_result.get('change_percentage', 0):.2f}%."
        
        try:
            print(f"Creating TRENDS analysis with title='Trend Analysis' ({len('Trend Analysis')} chars)")
            trends_analysis = Analysis.objects.create(
                analysis_type=Analysis.AnalysisType.TRENDS,
                analysis_title="Trend Analysis",
                analysis_summary=json.dumps(trends_result),
                generate_chart=generate_charts,
                report=report
            )
            print(f"✓ TRENDS analysis created: {trends_analysis.analysis_id}")
        except Exception as e:
            print(f"✗ TRENDS analysis error: {type(e).__name__}: {str(e)}")
            raise
        
        # Generuj wykres dla trendów jeśli zaznaczone
        if generate_charts:
            ReportManager._create_trend_chart(trends_analysis, readings)
        
        # === ANALIZA SZCZYTÓW ===
        peak_result = AnalysisUtils.calculate_peak_load(readings)
        
        # Generuj opis dla analysis_summary - AI lub statyczny
        if use_ai:
            ai_description_peak = AIGenerator.generate_analysis_description(
                'PEAK',
                peak_result,
                len(readings)
            )
            if ai_description_peak:
                print(f"✓ PEAK AI: {len(ai_description_peak)} chars: {ai_description_peak[:100]}")
                peak_result['summary'] = ai_description_peak
            else:
                print("✗ PEAK AI: brak opisu - używam statycznego")
                peak_result['summary'] = f"Analiza szczytów obciążenia. Maksymalna wartość: {peak_result.get('peak_value', 'N/A')}, średnia: {peak_result.get('average_value', 'N/A'):.2f}."
        else:
            print("ℹ PEAK: używam statycznego podsumowania")
            peak_result['summary'] = f"Analiza szczytów obciążenia. Maksymalna wartość: {peak_result.get('peak_value', 'N/A')}, średnia: {peak_result.get('average_value', 'N/A'):.2f}."
        
        peak_analysis = Analysis.objects.create(
            analysis_type=Analysis.AnalysisType.PEAK,
            analysis_title="Peak Load Analysis",
            analysis_summary=json.dumps(peak_result),
            generate_chart=generate_charts,
            report=report
        )
        
        # Generuj wykres dla szczytów jeśli zaznaczone
        if generate_charts:
            ReportManager._create_peak_chart(peak_analysis, readings)
    
    @staticmethod
    def generate_anomaly_analysis(
        report: Report,
        title: str = "Anomaly Detection",
        description: str = "Detection of anomalies and unusual patterns",
        generate_chart: bool = False,
        use_ai: bool = False
    ) -> Analysis:
        """
        Generuje analizę anomalii dla istniejącego raportu
        Wywoływane ręcznie przez użytkownika lub przez scheduled task
        
        Args:
            report: Raport dla którego tworzymy analizę anomalii
            title: Tytuł analizy
            description: Opis analizy
            generate_chart: Czy generować wykres
            use_ai: Czy używać AI do generowania opisów
            
        Returns:
            Utworzona analiza ANOMALY z prawdziwymi obliczeniami
        """
        # Sprawdź czy analiza anomalii już nie istnieje
        existing = Analysis.objects.filter(
            report=report,
            analysis_type=Analysis.AnalysisType.ANOMALY
        ).first()
        
        if existing:
            return existing
        
        # Pobierz dane z raportu
        readings = report.data_for_analysis.get('readings', [])
        
        if not readings:
            # Jeśli brak danych, zwróć pustą analizę
            anomaly_analysis = Analysis.objects.create(
                analysis_type=Analysis.AnalysisType.ANOMALY,
                analysis_title=title,
                analysis_summary=json.dumps({"error": "No data available for anomaly detection"}),
                generate_chart=False,
                report=report
            )
            return anomaly_analysis
        
        # Wykonaj prawdziwą detekcję anomalii
        anomaly_result = AnalysisUtils.detect_anomalies(readings)
        
        # Generuj opis dla analysis_summary - AI lub statyczny
        if use_ai:
            ai_description_anomaly = AIGenerator.generate_analysis_description(
                'ANOMALY',
                anomaly_result,
                len(readings)
            )
            if ai_description_anomaly:
                print(f"✓ ANOMALY AI: {len(ai_description_anomaly)} chars: {ai_description_anomaly[:100]}")
                anomaly_result['summary'] = ai_description_anomaly
            else:
                print("✗ ANOMALY AI: brak opisu - używam statycznego")
                anomaly_count = len(anomaly_result.get('anomalies', []))
                anomaly_result['summary'] = f"Wykryto {anomaly_count} anomalii w {len(readings)} pomiarach. Metoda detekcji: IQR (Interquartile Range)."
        else:
            print("ℹ ANOMALY: używam statycznego podsumowania")
            anomaly_count = len(anomaly_result.get('anomalies', []))
            anomaly_result['summary'] = f"Wykryto {anomaly_count} anomalii w {len(readings)} pomiarach. Metoda detekcji: IQR (Interquartile Range)."
        
        # Utwórz nową analizę anomalii z wynikami obliczeń
        anomaly_analysis = Analysis.objects.create(
            analysis_type=Analysis.AnalysisType.ANOMALY,
            analysis_title=title,
            analysis_summary=json.dumps(anomaly_result),
            generate_chart=generate_chart,
            report=report
        )
        
        # Generuj wykres jeśli zaznaczone
        if generate_chart:
            ReportManager._create_anomaly_chart(anomaly_analysis, readings, anomaly_result)
        
        return anomaly_analysis
    
    @staticmethod
    def _create_trend_chart(analysis: Analysis, readings: List[Dict[str, Any]]) -> Visualization:
        """
        Tworzy wykres dla analizy trendów
        
        Args:
            analysis: Obiekt Analysis
            readings: Lista odczytów
            
        Returns:
            Utworzona wizualizacja
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Backend bez GUI
            import matplotlib.pyplot as plt
            import seaborn as sns
            from datetime import datetime
            import os
            from django.conf import settings
            import matplotlib.dates as mdates
            
            # Ustaw styl seaborn
            sns.set_style("whitegrid")
            sns.set_palette("husl")
            
            # Przygotuj dane
            timestamps = []
            values = []
            for r in sorted(readings, key=lambda x: x.get('timestamp', '')):
                if r.get('timestamp') and r.get('value') is not None:
                    try:
                        ts = datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00'))
                        timestamps.append(ts)
                        values.append(r['value'])
                    except:
                        continue
            
            if not timestamps:
                return None
            
            # Twórz wykres
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Wykres liniowy z gradientem
            ax.plot(timestamps, values, marker='o', linestyle='-', linewidth=2.5, 
                   markersize=6, color='#2E86AB', markerfacecolor='#A23B72', 
                   markeredgewidth=1.5, markeredgecolor='#2E86AB', alpha=0.9)
            
            # Fill area pod wykresem
            ax.fill_between(timestamps, values, alpha=0.2, color='#2E86AB')
            
            # Tytuł i etykiety
            ax.set_title('Analiza Trendu', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Czas', fontsize=12, fontweight='bold')
            ax.set_ylabel('Wartość [kW]', fontsize=12, fontweight='bold')
            
            # Formatowanie osi X - pokaż tylko co n-ty timestamp
            if len(timestamps) > 10:
                step = max(1, len(timestamps) // 10)
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            plt.xticks(rotation=45, ha='right')
            
            # Siatka
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
            ax.set_axisbelow(True)
            
            # Ramka
            for spine in ax.spines.values():
                spine.set_edgecolor('#CCCCCC')
                spine.set_linewidth(1.2)
            
            plt.tight_layout()
            
            # Zapisz wykres
            media_root = getattr(settings, 'MEDIA_ROOT', '/app/media')
            charts_dir = os.path.join(media_root, 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            filename = f'trend_{analysis.analysis_id}.png'
            filepath = os.path.join(charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Utwórz wizualizację
            visualization = Visualization.objects.create(
                chart_title=f"Trend Chart - {analysis.analysis_title}",
                file_path=f'/media/charts/{filename}',
                analysis=analysis
            )
            
            return visualization
            
        except Exception as e:
            print(f"Error creating trend chart: {e}")
            return None
    
    @staticmethod
    def _create_peak_chart(analysis: Analysis, readings: List[Dict[str, Any]]) -> Visualization:
        """
        Tworzy wykres dla analizy szczytów
        
        Args:
            analysis: Obiekt Analysis
            readings: Lista odczytów
            
        Returns:
            Utworzona wizualizacja
        """
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import seaborn as sns
            import os
            from django.conf import settings
            from datetime import datetime
            import matplotlib.dates as mdates
            
            # Ustaw styl seaborn
            sns.set_style("whitegrid")
            
            # Przygotuj dane
            timestamps = []
            values = []
            for r in sorted(readings, key=lambda x: x.get('timestamp', '')):
                if r.get('timestamp') and r.get('value') is not None:
                    try:
                        ts = datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00'))
                        timestamps.append(ts)
                        values.append(r['value'])
                    except:
                        continue
            
            if not timestamps or not values:
                return None
            
            # Znajdź szczyt
            max_value = max(values)
            max_idx = values.index(max_value)
            threshold = max_value * 0.9
            avg_value = sum(values) / len(values)
            
            # Twórz wykres
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Wykres liniowy
            ax.plot(timestamps, values, marker='o', linestyle='-', linewidth=2.5,
                   markersize=6, color='#F18F01', label='Obciążenie',
                   markerfacecolor='#C73E1D', markeredgewidth=1.5, 
                   markeredgecolor='#F18F01', alpha=0.9)
            
            # Zaznacz szczyt
            ax.scatter([timestamps[max_idx]], [max_value], color='#C73E1D', 
                      s=200, marker='*', zorder=5, label=f'Szczyt: {max_value:.2f} kW',
                      edgecolors='white', linewidths=2)
            
            # Linie progowe
            ax.axhline(y=threshold, color='#E63946', linestyle='--', linewidth=2.5,
                      label=f'Prog (90%): {threshold:.2f} kW', alpha=0.7)
            ax.axhline(y=avg_value, color='#06A77D', linestyle='-.', linewidth=2,
                      label=f'Średnia: {avg_value:.2f} kW', alpha=0.7)
            
            # Fill area
            ax.fill_between(timestamps, values, avg_value, 
                           where=[v >= threshold for v in values],
                           alpha=0.3, color='#E63946', label='Strefa szczytowa')
            
            # Tytuł i etykiety
            ax.set_title('Analiza Szczytów Obciążenia', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Czas', fontsize=12, fontweight='bold')
            ax.set_ylabel('Obciążenie [kW]', fontsize=12, fontweight='bold')
            
            # Formatowanie osi X
            if len(timestamps) > 10:
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            plt.xticks(rotation=45, ha='right')
            
            # Legenda
            ax.legend(loc='upper left', framealpha=0.95, fontsize=10)
            
            # Siatka
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
            ax.set_axisbelow(True)
            
            # Ramka
            for spine in ax.spines.values():
                spine.set_edgecolor('#CCCCCC')
                spine.set_linewidth(1.2)
            
            plt.tight_layout()
            
            # Zapisz wykres
            media_root = getattr(settings, 'MEDIA_ROOT', '/app/media')
            charts_dir = os.path.join(media_root, 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            filename = f'peak_{analysis.analysis_id}.png'
            filepath = os.path.join(charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Utwórz wizualizację
            visualization = Visualization.objects.create(
                chart_title=f"Peak Load Chart - {analysis.analysis_title}",
                file_path=f'/media/charts/{filename}',
                analysis=analysis
            )
            
            return visualization
            
        except Exception as e:
            print(f"Error creating peak chart: {e}")
            return None
    
    @staticmethod
    def _create_anomaly_chart(analysis: Analysis, readings: List[Dict[str, Any]], anomaly_result: Dict[str, Any]) -> Visualization:
        """
        Tworzy wykres dla analizy anomalii
        
        Args:
            analysis: Obiekt Analysis
            readings: Lista odczytów
            anomaly_result: Wyniki detekcji anomalii
            
        Returns:
            Utworzona wizualizacja
        """
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import seaborn as sns
            import os
            from django.conf import settings
            from datetime import datetime
            import matplotlib.dates as mdates
            
            # Ustaw styl seaborn
            sns.set_style("whitegrid")
            
            # Przygotuj dane
            timestamps = []
            values = []
            for r in sorted(readings, key=lambda x: x.get('timestamp', '')):
                if r.get('timestamp') and r.get('value') is not None:
                    try:
                        ts = datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00'))
                        timestamps.append(ts)
                        values.append(r['value'])
                    except:
                        continue
            
            if not timestamps or not values:
                return None
            
            # Wyciągnij anomalie z wyniku
            anomalies = anomaly_result.get('anomalies', [])
            anomaly_indices = [a.get('index') for a in anomalies if 'index' in a]
            
            # Wartości średnie i granice
            stats = anomaly_result.get('statistics', {})
            mean = stats.get('mean', sum(values)/len(values)) if stats else sum(values)/len(values)
            std_dev = stats.get('std', 0) if stats else 0
            upper_bound = mean + 2.5 * std_dev if std_dev > 0 else mean * 1.2
            lower_bound = mean - 2.5 * std_dev if std_dev > 0 else mean * 0.8
            
            # Twórz wykres
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Wykres liniowy
            ax.plot(timestamps, values, marker='o', linestyle='-', linewidth=2.5,
                   markersize=5, color='#4361EE', label='Pomiary',
                   markerfacecolor='#7209B7', markeredgewidth=1.5,
                   markeredgecolor='#4361EE', alpha=0.8)
            
            # Zaznacz anomalie
            if anomaly_indices:
                anomaly_times = [timestamps[i] for i in anomaly_indices if i < len(timestamps)]
                anomaly_values = [values[i] for i in anomaly_indices if i < len(values)]
                ax.scatter(anomaly_times, anomaly_values, color='#D62828', s=200,
                          marker='X', label=f'Anomalie ({len(anomaly_indices)})',
                          zorder=5, edgecolors='white', linewidths=2)
            
            # Linie granic - strefy
            ax.fill_between(timestamps, upper_bound, lower_bound, 
                           alpha=0.15, color='#06A77D', label='Strefa normalna')
            
            ax.axhline(y=mean, color='#06A77D', linestyle='-', linewidth=2.5,
                      label=f'Średnia: {mean:.2f} kW', alpha=0.8)
            ax.axhline(y=upper_bound, color='#F77F00', linestyle='--', linewidth=2,
                      label=f'Górny próg: {upper_bound:.2f} kW', alpha=0.7)
            ax.axhline(y=lower_bound, color='#F77F00', linestyle='--', linewidth=2,
                      label=f'Dolny próg: {lower_bound:.2f} kW', alpha=0.7)
            
            # Tytuł i etykiety
            ax.set_title('Detekcja Anomalii', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Czas', fontsize=12, fontweight='bold')
            ax.set_ylabel('Wartość [kW]', fontsize=12, fontweight='bold')
            
            # Formatowanie osi X
            if len(timestamps) > 10:
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            plt.xticks(rotation=45, ha='right')
            
            # Legenda
            ax.legend(loc='upper left', framealpha=0.95, fontsize=10)
            
            # Siatka
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
            ax.set_axisbelow(True)
            
            # Ramka
            for spine in ax.spines.values():
                spine.set_edgecolor('#CCCCCC')
                spine.set_linewidth(1.2)
            
            plt.tight_layout()
            
            # Zapisz wykres
            media_root = getattr(settings, 'MEDIA_ROOT', '/app/media')
            charts_dir = os.path.join(media_root, 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            filename = f'anomaly_{analysis.analysis_id}.png'
            filepath = os.path.join(charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Utwórz wizualizację
            visualization = Visualization.objects.create(
                chart_title=f"Anomaly Detection Chart - {analysis.analysis_title}",
                file_path=f'/media/charts/{filename}',
                analysis=analysis
            )
            
            return visualization
            
        except Exception as e:
            print(f"Error creating anomaly chart: {e}")
            return None
    
    # ========== Report Comparison ==========
    
    @staticmethod
    def compare_reports(report_one: Report, report_two: Report, generate_chart: bool = False) -> ReportCompare:
        """
        Porównuje dwa raporty i tworzy obiekt ReportCompare
        
        Args:
            report_one: Pierwszy raport
            report_two: Drugi raport
            generate_chart: Czy generować wykres porównawczy
        
        Returns:
            Obiekt ReportCompare z wynikami porównania i opcjonalnym wykresem
        """
        # Pobierz dane z obu raportów
        data_one = report_one.data_for_analysis.get('readings', [])
        data_two = report_two.data_for_analysis.get('readings', [])
        
        # Oblicz statystyki porównawcze
        comparison_stats = AnalysisUtils.compare_periods(data_one, data_two)
        
        # Generuj opis porównania z statystykami
        compare_description = ReportManager._generate_comparison_description(
            report_one, 
            report_two,
            comparison_stats
        )
        
        # Twórz obiekt porównania
        report_compare = ReportCompare.objects.create(
            report_one=report_one,
            report_two=report_two,
            compare_description=compare_description
        )
        
        # Generuj wykres porównawczy jeśli zaznaczone
        if generate_chart:
            chart_path = ReportManager._create_comparison_chart(report_compare, data_one, data_two, comparison_stats)
            if chart_path:
                report_compare.visualization_file = chart_path
                report_compare.save()
        
        return report_compare
    
    @staticmethod
    def _generate_comparison_description(report_one: Report, report_two: Report, stats: Dict[str, Any]) -> str:
        """
        Generuje opis porównania dwóch raportów z statystykami
        """
        return json.dumps({
            "report_one": {
                "id": str(report_one.report_id),
                "period": f"{report_one.report_criteria.date_created_from if report_one.report_criteria else 'N/A'} - {report_one.report_criteria.date_created_to if report_one.report_criteria else 'N/A'}",
                "data_points": len(report_one.data_for_analysis.get('readings', []))
            },
            "report_two": {
                "id": str(report_two.report_id),
                "period": f"{report_two.report_criteria.date_created_from if report_two.report_criteria else 'N/A'} - {report_two.report_criteria.date_created_to if report_two.report_criteria else 'N/A'}",
                "data_points": len(report_two.data_for_analysis.get('readings', []))
            },
            "comparison": stats
        })
    
    @staticmethod
    def _create_comparison_chart(report_compare: ReportCompare, data_one: List[Dict[str, Any]], 
                                  data_two: List[Dict[str, Any]], stats: Dict[str, Any]) -> Optional[str]:
        """
        Tworzy wykres porównawczy dla dwóch raportów
        
        Args:
            report_compare: Obiekt ReportCompare
            data_one: Dane pierwszego raportu
            data_two: Dane drugiego raportu
            stats: Statystyki porównawcze
            
        Returns:
            Ścieżka do zapisanego pliku lub None
        """
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import os
            from django.conf import settings
            
            # Przygotuj dane - agreguj po czasie
            values_one = [r['value'] for r in data_one if 'value' in r and r['value'] is not None]
            values_two = [r['value'] for r in data_two if 'value' in r and r['value'] is not None]
            
            if not values_one or not values_two:
                return None
            
            # Twórz wykres z wieloma panelami
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Report Comparison', fontsize=16, fontweight='bold')
            
            # Panel 1: Line plot - porównanie wartości w czasie
            ax1 = axes[0, 0]
            ax1.plot(range(len(values_one)), values_one, marker='o', linestyle='-', 
                    linewidth=2, markersize=4, label='Report 1', color='blue', alpha=0.7)
            ax1.plot(range(len(values_two)), values_two, marker='s', linestyle='-', 
                    linewidth=2, markersize=4, label='Report 2', color='red', alpha=0.7)
            ax1.set_title('Values Over Time')
            ax1.set_xlabel('Reading Index')
            ax1.set_ylabel('Value')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Panel 2: Box plot - porównanie rozkładów
            ax2 = axes[0, 1]
            box_data = [values_one, values_two]
            bp = ax2.boxplot(box_data, labels=['Report 1', 'Report 2'], patch_artist=True)
            bp['boxes'][0].set_facecolor('blue')
            bp['boxes'][1].set_facecolor('red')
            for box in bp['boxes']:
                box.set_alpha(0.6)
            ax2.set_title('Distribution Comparison')
            ax2.set_ylabel('Value')
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Panel 3: Bar chart - statystyki porównawcze
            ax3 = axes[1, 0]
            categories = ['Mean', 'Median', 'Max', 'Min']
            report1_stats = [
                stats.get('period1_avg', 0),
                stats.get('period1_median', 0),
                stats.get('period1_max', 0),
                stats.get('period1_min', 0)
            ]
            report2_stats = [
                stats.get('period2_avg', 0),
                stats.get('period2_median', 0),
                stats.get('period2_max', 0),
                stats.get('period2_min', 0)
            ]
            x = range(len(categories))
            width = 0.35
            ax3.bar([i - width/2 for i in x], report1_stats, width, label='Report 1', color='blue', alpha=0.7)
            ax3.bar([i + width/2 for i in x], report2_stats, width, label='Report 2', color='red', alpha=0.7)
            ax3.set_title('Statistical Comparison')
            ax3.set_ylabel('Value')
            ax3.set_xticks(x)
            ax3.set_xticklabels(categories)
            ax3.legend()
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Panel 4: Tekstowe podsumowanie różnic
            ax4 = axes[1, 1]
            ax4.axis('off')
            summary_text = f"""
Comparison Summary:

Period 1 Average: {stats.get('period1_avg', 0):.2f}
Period 2 Average: {stats.get('period2_avg', 0):.2f}
Difference: {stats.get('difference', 0):.2f}
Percentage Change: {stats.get('percentage_change', 0):.2f}%

Period 1 Data Points: {len(values_one)}
Period 2 Data Points: {len(values_two)}

Trend: {stats.get('trend', 'N/A')}
            """.strip()
            ax4.text(0.1, 0.5, summary_text, transform=ax4.transAxes, 
                    fontsize=11, verticalalignment='center', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
            
            plt.tight_layout()
            
            # Zapisz wykres
            media_root = getattr(settings, 'MEDIA_ROOT', '/app/media')
            charts_dir = os.path.join(str(media_root), 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            filename = f'comparison_{report_compare.report_compare_id}.png'
            filepath = os.path.join(charts_dir, filename)
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Zwróć ścieżkę do pliku
            return f'/media/charts/{filename}'
            
        except Exception as e:
            print(f"Error creating comparison chart: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # ========== Export Operations ==========
    
    @staticmethod
    def export_report(report_id: str) -> Optional[Dict[str, Any]]:
        """
        Eksportuje raport do formatu JSON
        
        Args:
            report_id: UUID raportu
        
        Returns:
            Dict z danymi lub None
        """
        report = ReportManager.find_report_by_id(report_id)
        if not report:
            return None
        
        # Przygotuj dane do eksportu
        export_data = {
            "report_id": str(report.report_id),
            "created_timestamp": report.created_timestamp.isoformat(),
            "report_description": report.report_description,
            "criteria": {
                "location": report.report_criteria.location if report.report_criteria else None,
                "frequency": report.report_criteria.report_frequency if report.report_criteria else None,
                "date_from": str(report.report_criteria.date_created_from) if report.report_criteria else None,
                "date_to": str(report.report_criteria.date_created_to) if report.report_criteria else None,
                "device_type": report.report_criteria.device_type if report.report_criteria else None
            },
            "data_for_analysis": report.data_for_analysis,
            "analyses": [
                {
                    "analysis_id": str(analysis.analysis_id),
                    "type": analysis.analysis_type,
                    "title": analysis.analysis_title,
                    "summary": analysis.analysis_summary,
                    "visualizations": [
                        {
                            "visualization_id": str(viz.visualization_id),
                            "title": viz.chart_title,
                            "file_path": viz.file_path
                        }
                        for viz in analysis.visualizations.all()
                    ]
                }
                for analysis in report.analyses.all()
            ]
        }
        
        return export_data
    
    # ========== Visualization Operations ==========
    
    @staticmethod
    def generate_visualization(analysis: Analysis) -> Visualization:
        """
        Generuje wizualizację dla analizy
        
        Args:
            analysis: Obiekt Analysis
        
        Returns:
            Utworzona wizualizacja
        """
        visualization = Visualization.objects.create(
            chart_title=f"Chart for {analysis.analysis_title}",
            file_path=f"/visualizations/{analysis.analysis_id}/chart.png",
            analysis=analysis
        )
        
        return visualization
    
    @staticmethod
    def download_analysis_data(report_id: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera dane analityczne raportu
        
        Args:
            report_id: UUID raportu
        
        Returns:
            Słownik z danymi analitycznymi lub None
        """
        report = ReportManager.find_report_by_id(report_id)
        if not report:
            return None
        
        return {
            "report_id": str(report.report_id),
            "analysis_data": report.data_for_analysis,
            "analyses_summary": [
                {
                    "type": analysis.analysis_type,
                    "summary": analysis.analysis_summary
                }
                for analysis in report.analyses.all()
            ]
        }
    
    # ========== PDF Export Operations ==========
    
    @staticmethod
    def generate_pdf_report(report_id: str) -> Optional[str]:
        """
        Generuje kompletny raport w formacie PDF z polskimi znakami zawierający:
        - Opis raportu (report_description)
        - Wszystkie analizy z opisami AI (analysis_summary)
        - Wizualizacje (wykresy)
        
        Args:
            report_id: UUID raportu
        
        Returns:
            Ścieżka do wygenerowanego pliku PDF lub None
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        from django.conf import settings
        from datetime import datetime
        
        report = ReportManager.find_report_by_id(report_id)
        if not report:
            return None
        
        try:
            # Funkcja do konwersji polskich znaków na ASCII
            def fix_polish_chars(text):
                """Zamienia polskie znaki na ich odpowiedniki ASCII dla lepszej kompatybilności z Helvetica"""
                if not isinstance(text, str):
                    return str(text)
                polish_chars = {
                    'ą': 'a', 'Ą': 'A',
                    'ć': 'c', 'Ć': 'C',
                    'ę': 'e', 'Ę': 'E',
                    'ł': 'l', 'Ł': 'L',
                    'ń': 'n', 'Ń': 'N',
                    'ó': 'o', 'Ó': 'O',
                    'ś': 's', 'Ś': 'S',
                    'ź': 'z', 'Ź': 'Z',
                    'ż': 'z', 'Ż': 'Z'
                }
                for pl, ascii in polish_chars.items():
                    text = text.replace(pl, ascii)
                return text
            
            # Użyj standardowych czcionek
            font_name = 'Helvetica'
            font_bold = 'Helvetica-Bold'
            
            # Przygotuj ścieżkę do zapisu PDF
            media_root = getattr(settings, 'MEDIA_ROOT', '/app/media')
            pdf_dir = os.path.join(str(media_root), 'reports')
            os.makedirs(pdf_dir, exist_ok=True)
            
            filename = f'raport_{report_id}.pdf'
            filepath = os.path.join(pdf_dir, filename)
            
            # Utwórz dokument PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=40
            )
            
            # Kontener na elementy dokumentu
            story = []
            styles = getSampleStyleSheet()
            
            # Niestandardowe style z polskimi czcionkami
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=font_bold,
                fontSize=24,
                textColor=colors.HexColor('#1B4965'),
                spaceAfter=30,
                alignment=TA_CENTER,
                leading=30
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontName=font_name,
                fontSize=16,
                textColor=colors.HexColor('#5FA8D3'),
                spaceAfter=20,
                alignment=TA_CENTER,
                leading=20
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName=font_bold,
                fontSize=16,
                textColor=colors.HexColor('#1B4965'),
                spaceAfter=12,
                spaceBefore=20,
                leading=20,
                borderWidth=0,
                borderColor=colors.HexColor('#5FA8D3'),
                borderPadding=8,
                leftIndent=10
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubheading',
                parent=styles['Heading3'],
                fontName=font_bold,
                fontSize=13,
                textColor=colors.HexColor('#2E86AB'),
                spaceAfter=8,
                spaceBefore=12,
                leading=16
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                spaceAfter=10,
                textColor=colors.HexColor('#2B2D42')
            )
            
            bold_style = ParagraphStyle(
                'CustomBold',
                parent=normal_style,
                fontName=font_bold,
                textColor=colors.HexColor('#1B4965')
            )
            
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=normal_style,
                fontSize=10,
                textColor=colors.HexColor('#6C757D'),
                alignment=TA_LEFT
            )
            
            # ===== Strona tytułowa =====
            # Tytuł główny
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(fix_polish_chars("SYSTEM ZARZADZANIA ENERGIA"), title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Linia oddzielająca
            line_data = [['']]
            line_table = Table(line_data, colWidths=[7*inch])
            line_table.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 3, colors.HexColor('#5FA8D3')),
                ('LINEBELOW', (0, 0), (-1, 0), 3, colors.HexColor('#5FA8D3')),
            ]))
            story.append(line_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Subtitle
            story.append(Paragraph(fix_polish_chars("Raport Analityczny Energetyczny"), subtitle_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Informacje podstawowe - nowoczesna tabela
            info_data = [
                [Paragraph(fix_polish_chars("<b>ID Raportu:</b>"), info_style), 
                 Paragraph(str(report.report_id), normal_style)],
                [Paragraph(fix_polish_chars("<b>Data wygenerowania:</b>"), info_style), 
                 Paragraph(report.created_timestamp.strftime("%d.%m.%Y %H:%M:%S"), normal_style)],
                [Paragraph(fix_polish_chars("<b>Okres analizy:</b>"), info_style), 
                 Paragraph(f"{report.report_criteria.date_created_from if report.report_criteria else 'N/A'} - {report.report_criteria.date_created_to if report.report_criteria else 'N/A'}", normal_style)],
            ]
            
            if report.report_criteria:
                if report.report_criteria.location:
                    info_data.append([Paragraph(fix_polish_chars("<b>Lokalizacja:</b>"), info_style), 
                                     Paragraph(report.report_criteria.location, normal_style)])
                if report.report_criteria.device_type:
                    info_data.append([Paragraph(fix_polish_chars("<b>Typ urzadzenia:</b>"), info_style), 
                                     Paragraph(report.report_criteria.device_type, normal_style)])
                if report.report_criteria.report_frequency:
                    info_data.append([Paragraph(fix_polish_chars("<b>Czestotliwosc:</b>"), info_style), 
                                     Paragraph(report.report_criteria.get_report_frequency_display(), normal_style)])
            
            info_table = Table(info_data, colWidths=[2.5*inch, 4.5*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.4*inch))
            
            # Podsumowanie wykonawcze - z ramką
            if report.report_description:
                story.append(Paragraph(fix_polish_chars("Podsumowanie Wykonawcze"), heading_style))
                story.append(Spacer(1, 0.1*inch))
                
                summary_box = Table([[Paragraph(fix_polish_chars(report.report_description), normal_style)]], 
                                   colWidths=[7*inch])
                summary_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F4F8')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#5FA8D3')),
                ]))
                story.append(summary_box)
                story.append(Spacer(1, 0.3*inch))
            
            # ===== Podsumowanie danych =====
            story.append(Paragraph("Podsumowanie Danych", heading_style))
            
            # Pobierz dane z raportu
            readings = report.data_for_analysis.get('readings', [])
            if readings:
                values = [r['value'] for r in readings if 'value' in r]
                
                if values:
                    import statistics
                    
                    # Użyj Paragraph dla wszystkich komórek z polskimi znakami
                    summary_data = [
                        [Paragraph(fix_polish_chars("<b>Liczba pomiarow:</b>"), bold_style), 
                         Paragraph(str(len(readings)), normal_style)],
                        [Paragraph(fix_polish_chars("<b>Wartosc minimalna:</b>"), bold_style), 
                         Paragraph(f"{min(values):.2f} kW", normal_style)],
                        [Paragraph(fix_polish_chars("<b>Wartosc maksymalna:</b>"), bold_style), 
                         Paragraph(f"{max(values):.2f} kW", normal_style)],
                        [Paragraph(fix_polish_chars("<b>Wartosc srednia:</b>"), bold_style), 
                         Paragraph(f"{statistics.mean(values):.2f} kW", normal_style)],
                        [Paragraph(fix_polish_chars("<b>Mediana:</b>"), bold_style), 
                         Paragraph(f"{statistics.median(values):.2f} kW", normal_style)],
                    ]
                    
                    if len(values) > 1:
                        summary_data.append([
                            Paragraph(fix_polish_chars("<b>Odchylenie standardowe:</b>"), bold_style), 
                            Paragraph(f"{statistics.stdev(values):.2f} kW", normal_style)
                        ])
                    
                    summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
                    summary_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#5FA8D3')),
                    ]))
                    story.append(summary_table)
                    story.append(Spacer(1, 0.3*inch))
            
            story.append(PageBreak())
            
            # ===== Analizy =====
            analyses = report.analyses.all().order_by('analysis_type')
            
            for idx, analysis in enumerate(analyses):
                # Tytuł analizy
                analysis_type_names = {
                    'TRENDS': fix_polish_chars('Analiza Trendow'),
                    'PEAK': fix_polish_chars('Analiza Szczytow Obciazenia'),
                    'ANOMALY': fix_polish_chars('Detekcja Anomalii')
                }
                analysis_name = analysis_type_names.get(analysis.analysis_type, analysis.get_analysis_type_display())
                
                story.append(Paragraph(fix_polish_chars(analysis_name), heading_style))
                story.append(Spacer(1, 0.15*inch))
                
                # Parsuj JSON summary
                try:
                    summary_data = json.loads(analysis.analysis_summary) if isinstance(analysis.analysis_summary, str) else analysis.analysis_summary
                    
                    # Wyświetl podsumowanie jeśli istnieje (AI lub statyczne)
                    if isinstance(summary_data, dict) and 'summary' in summary_data:
                        summary_text = summary_data['summary']
                        story.append(Paragraph(fix_polish_chars("<b>Podsumowanie:</b>"), bold_style))
                        story.append(Spacer(1, 0.05*inch))
                        story.append(Paragraph(fix_polish_chars(summary_text), normal_style))
                        story.append(Spacer(1, 0.2*inch))
                    
                    # Wyświetl szczegóły techniczne
                    if isinstance(summary_data, dict):
                        story.append(Paragraph(fix_polish_chars("<b>Szczegoly:</b>"), bold_style))
                        story.append(Spacer(1, 0.05*inch))
                        
                        # Mapowanie kluczy na nazwy bez polskich znaków
                        key_translations = {
                            'trend': 'Trend',
                            'trend_direction': 'Kierunek trendu',
                            'change_percentage': 'Zmiana procentowa',
                            'first_period_avg': 'Srednia pierwszego okresu',
                            'second_period_avg': 'Srednia drugiego okresu',
                            'absolute_change': 'Zmiana bezwzgledna',
                            'peak_value': 'Wartosc szczytowa',
                            'peak_timestamp': 'Czas szczytu',
                            'peak_location': 'Lokalizacja',
                            'peak_device': 'ID urzadzenia',
                            'peak_metric': 'Metryka',
                            'average_value': 'Wartosc srednia',
                            'peak_events_count': 'Liczba przekroczen',
                            'peak_threshold': 'Prog',
                            'anomaly_count': 'Liczba anomalii',
                            'anomaly_indices': 'Indeksy anomalii',
                            'statistics': 'Statystyki'
                        }
                        
                        summary_items = []
                        for key, value in summary_data.items():
                            if key == 'summary':
                                continue  # Już wyświetlono wyżej
                            if isinstance(value, (dict, list)):
                                continue  # Pomijamy zagnieżdżone struktury
                            
                            label = key_translations.get(key, str(key).replace('_', ' ').title())
                            
                            # Formatuj wartość
                            if isinstance(value, float):
                                formatted_value = f"{value:.2f}"
                            else:
                                formatted_value = str(value)
                            
                            # Użyj Paragraph dla poprawnego wyświetlania polskich znaków
                            summary_items.append([
                                Paragraph(fix_polish_chars(f"<b>{label}:</b>"), bold_style),
                                Paragraph(fix_polish_chars(formatted_value), normal_style)
                            ])
                        
                        if summary_items:
                            details_table = Table(summary_items, colWidths=[2.8*inch, 3*inch])
                            details_table.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('TOPPADDING', (0, 0), (-1, -1), 8),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                            ]))
                            story.append(details_table)
                            story.append(Spacer(1, 0.25*inch))
                
                except (json.JSONDecodeError, TypeError) as e:
                    story.append(Paragraph(str(analysis.analysis_summary), normal_style))
                    story.append(Spacer(1, 0.2*inch))
                
                # Wizualizacje
                visualizations = analysis.visualizations.all()
                for viz in visualizations:
                    if viz.file_path:
                        try:
                            # Usuń /media/ z ścieżki
                            img_path = viz.file_path.replace('/media/', '')
                            full_img_path = os.path.join(media_root, img_path)
                            
                            if os.path.exists(full_img_path):
                                story.append(Paragraph(fix_polish_chars("<b>Wykres:</b>"), bold_style))
                                story.append(Spacer(1, 0.1*inch))
                                
                                # Dodaj obraz z dostosowaniem rozmiaru
                                img = Image(full_img_path, width=6.5*inch, height=3.5*inch)
                                story.append(img)
                                story.append(Spacer(1, 0.2*inch))
                        except Exception as e:
                            print(f"Blad dodawania wizualizacji {viz.visualization_id}: {e}")
                
                # Separator między analizami
                if idx < len(analyses) - 1:
                    story.append(PageBreak())
            
            # Generuj PDF
            doc.build(story)
            
            return f'/media/reports/{filename}'
            
        except Exception as e:
            print(f"Blad generowania PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def generate_comparison_pdf(comparison_id: str) -> Optional[str]:
        """
        Generuje raport PDF dla porównania dwóch raportów zawierający:
        - Metadane obu raportów
        - Statystyki porównawcze
        - Wykres porównawczy (jeśli istnieje)
        
        Args:
            comparison_id: UUID porównania (ReportCompare)
        
        Returns:
            Ścieżka do wygenerowanego pliku PDF lub None
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import os
        from django.conf import settings
        
        try:
            comparison = ReportCompare.objects.select_related(
                'report_one__report_criteria',
                'report_two__report_criteria'
            ).get(report_compare_id=comparison_id)
        except ReportCompare.DoesNotExist:
            return None
        
        try:
            # Przygotuj ścieżkę do zapisu PDF
            media_root = getattr(settings, 'MEDIA_ROOT', '/app/media')
            pdf_dir = os.path.join(str(media_root), 'reports')
            os.makedirs(pdf_dir, exist_ok=True)
            
            filename = f'comparison_{comparison_id}.pdf'
            filepath = os.path.join(pdf_dir, filename)
            
            # Utwórz dokument PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Kontener na elementy dokumentu
            story = []
            styles = getSampleStyleSheet()
            
            # Niestandardowe style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c5aa0'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # ===== Strona tytułowa =====
            story.append(Paragraph("Energy Management System", title_style))
            story.append(Paragraph("Report Comparison", title_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Informacje podstawowe
            info_data = [
                ["Comparison ID:", str(comparison.report_compare_id)],
                ["Generated:", comparison.created_timestamp.strftime("%Y-%m-%d %H:%M:%S")],
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c5aa0')),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))
            
            # ===== Informacje o raportach =====
            story.append(Paragraph("Compared Reports", heading_style))
            
            # Report 1
            report1_data = [
                ["Report 1 ID:", str(comparison.report_one.report_id)],
                ["Period:", f"{comparison.report_one.report_criteria.date_created_from if comparison.report_one.report_criteria else 'N/A'} - {comparison.report_one.report_criteria.date_created_to if comparison.report_one.report_criteria else 'N/A'}"],
            ]
            if comparison.report_one.report_criteria:
                if comparison.report_one.report_criteria.location:
                    report1_data.append(["Location:", comparison.report_one.report_criteria.location])
                if comparison.report_one.report_criteria.device_type:
                    report1_data.append(["Device Type:", comparison.report_one.report_criteria.device_type])
            
            report1_table = Table(report1_data, colWidths=[2*inch, 4*inch])
            report1_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f2ff')),
            ]))
            story.append(report1_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Report 2
            report2_data = [
                ["Report 2 ID:", str(comparison.report_two.report_id)],
                ["Period:", f"{comparison.report_two.report_criteria.date_created_from if comparison.report_two.report_criteria else 'N/A'} - {comparison.report_two.report_criteria.date_created_to if comparison.report_two.report_criteria else 'N/A'}"],
            ]
            if comparison.report_two.report_criteria:
                if comparison.report_two.report_criteria.location:
                    report2_data.append(["Location:", comparison.report_two.report_criteria.location])
                if comparison.report_two.report_criteria.device_type:
                    report2_data.append(["Device Type:", comparison.report_two.report_criteria.device_type])
            
            report2_table = Table(report2_data, colWidths=[2*inch, 4*inch])
            report2_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffe6e6')),
            ]))
            story.append(report2_table)
            story.append(Spacer(1, 0.3*inch))
            
            # ===== Statystyki porównawcze =====
            if comparison.compare_description:
                story.append(Paragraph("Detailed Comparison Statistics", heading_style))
                
                try:
                    compare_data = json.loads(comparison.compare_description) if isinstance(comparison.compare_description, str) else comparison.compare_description
                    
                    if 'comparison' in compare_data and isinstance(compare_data['comparison'], dict):
                        stats = compare_data['comparison']
                        
                        # Tabela porównawcza w stylu z show_comparison_details.py
                        comparison_table_data = [
                            ["Metric", "Report 1", "Report 2"],
                            ["Average (kW)", f"{stats.get('period1_avg', 0):.2f}", f"{stats.get('period2_avg', 0):.2f}"],
                            ["Median (kW)", f"{stats.get('period1_median', 0):.2f}", f"{stats.get('period2_median', 0):.2f}"],
                            ["Minimum (kW)", f"{stats.get('period1_min', 0):.2f}", f"{stats.get('period2_min', 0):.2f}"],
                            ["Maximum (kW)", f"{stats.get('period1_max', 0):.2f}", f"{stats.get('period2_max', 0):.2f}"],
                        ]
                        
                        comparison_table = Table(comparison_table_data, colWidths=[2*inch, 2*inch, 2*inch])
                        comparison_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#e6f2ff')),
                            ('BACKGROUND', (2, 1), (2, -1), colors.HexColor('#ffe6e6')),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2c5aa0')),
                        ]))
                        story.append(comparison_table)
                        story.append(Spacer(1, 0.3*inch))
                        
                        # Analiza zmian
                        story.append(Paragraph("<b>Change Analysis:</b>", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                        
                        change_data = [
                            ["Absolute difference:", f"{stats.get('difference', 0):.2f} kW"],
                            ["Percentage change:", f"{stats.get('percentage_change', 0):.2f}%"],
                            ["Trend direction:", str(stats.get('trend_direction', 'N/A')).upper()],
                            ["Trend:", str(stats.get('trend', 'N/A'))]
                        ]
                        
                        change_table = Table(change_data, colWidths=[2.5*inch, 2*inch])
                        change_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9e6')),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcc00')),
                        ]))
                        story.append(change_table)
                        story.append(Spacer(1, 0.3*inch))
                        
                        # Wnioski
                        story.append(Paragraph("<b>Key Findings:</b>", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                        
                        avg_change = stats.get('percentage_change', 0)
                        trend = stats.get('trend', 'stable')
                        avg1 = stats.get('period1_avg', 0)
                        avg2 = stats.get('period2_avg', 0)
                        max1 = stats.get('period1_max', 0)
                        max2 = stats.get('period2_max', 0)
                        
                        if avg_change > 0:
                            change_desc = "increase"
                        elif avg_change < 0:
                            change_desc = "decrease"
                        else:
                            change_desc = "no significant change"
                        
                        findings_text = f"""
                        • In Period 2, an energy consumption <b>{change_desc}</b> of <b>{abs(avg_change):.1f}%</b> was observed<br/>
                        • Average consumption changed from <b>{avg1:.1f} kW</b> to <b>{avg2:.1f} kW</b><br/>
                        • Peak consumption changed from <b>{max1:.1f} kW</b> to <b>{max2:.1f} kW</b><br/>
                        • Overall trend: <b>{trend.upper()}</b>
                        """
                        
                        story.append(Paragraph(findings_text, styles['Normal']))
                        story.append(Spacer(1, 0.3*inch))
                        
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Error parsing comparison description: {e}")
            
            # ===== Wykres porównawczy =====
            if comparison.visualization_file:
                story.append(PageBreak())
                story.append(Paragraph("Comparison Visualization", heading_style))
                story.append(Spacer(1, 0.2*inch))
                
                try:
                    img_path = comparison.visualization_file.replace('/media/', '')
                    full_img_path = os.path.join(media_root, img_path)
                    
                    if os.path.exists(full_img_path):
                        # Dodaj obraz z większym rozmiarem (pełna szerokość strony)
                        img = Image(full_img_path, width=6.5*inch, height=4.5*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                        story.append(Paragraph(
                            "<i>Figure: 4-panel comparison chart showing line plot, box plot, bar chart, and statistical summary</i>",
                            styles['Normal']
                        ))
                except Exception as e:
                    print(f"Error adding comparison visualization: {e}")
            
            # Generuj PDF
            doc.build(story)
            
            return f'/media/reports/{filename}'
            
        except Exception as e:
            print(f"Error generating comparison PDF: {e}")
            import traceback
            traceback.print_exc()
            return None


# ============================================================================
#                           REST API VIEWSETS
# ============================================================================

class ReportCriteriaViewSet(viewsets.ModelViewSet):
    """ViewSet dla kryteriów raportów"""
    queryset = ReportCriteria.objects.all()
    serializer_class = ReportCriteriaSerializer
    authentication_classes = []
    permission_classes = []


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet dla raportów z dodatkowymi akcjami"""
    queryset = Report.objects.prefetch_related(
        'analyses__visualizations',
        'report_criteria'
    ).all()
    serializer_class = ReportSerializer
    authentication_classes = []
    permission_classes = []
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Endpoint do generowania nowego raportu
        Automatycznie tworzy analizy TRENDS i PEAK
        
        POST /analysis-reporting/reports/generate/
        Body: {
            "criteria_id": "uuid",
            "generate_charts": true/false  (opcjonalne, domyślnie false),
            "use_ai": true/false  (opcjonalne, domyślnie false)
        }
        """
        criteria_id = request.data.get('criteria_id')
        generate_charts = request.data.get('generate_charts', False)
        use_ai = request.data.get('use_ai', False)
        
        if not criteria_id:
            return Response(
                {"error": "criteria_id jest wymagane"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            criteria = ReportCriteria.objects.get(report_criteria_id=criteria_id)
            report = ReportManager.generate_report(criteria, generate_charts, use_ai)
            serializer = self.get_serializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ReportCriteria.DoesNotExist:
            return Response(
                {"error": "Kryteria nie znalezione"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return Response(
                {
                    "error": f"Błąd podczas generowania raportu: {str(e)}",
                    "type": type(e).__name__,
                    "traceback": tb
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def generate_anomaly(self, request, pk=None):
        """
        Endpoint do generowania analizy anomalii dla istniejącego raportu
        Wywoływane ręcznie przez użytkownika
        
        POST /analysis-reporting/reports/{id}/generate_anomaly/
        Body: {
            "generate_chart": true/false  (opcjonalne, domyślnie true),
            "use_ai": true/false  (opcjonalne, domyślnie false)
        }
        """
        report = self.get_object()
        generate_chart = request.data.get('generate_chart', True)
        use_ai = request.data.get('use_ai', False)
        
        try:
            anomaly_analysis = ReportManager.generate_anomaly_analysis(
                report=report,
                generate_chart=generate_chart,
                use_ai=use_ai
            )
            from .serializers import AnalysisSerializer
            serializer = AnalysisSerializer(anomaly_analysis)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """
        Endpoint do eksportu pełnego raportu z analizami
        GET /analysis-reporting/reports/{id}/export/
        """
        export_data = ReportManager.export_report(pk)
        if export_data:
            return Response(export_data)
        return Response(
            {"error": "Report not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=True, methods=['get'])
    def export_data(self, request, pk=None):
        """
        Endpoint do eksportu tylko czystych danych pomiarowych
        GET /analysis-reporting/reports/{id}/export_data/
        """
        report = self.get_object()
        if not report:
            return Response(
                {"error": "Report not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Zwróć tylko data_for_analysis (czyste dane pomiarowe)
        return Response(report.data_for_analysis)
    
    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """
        Endpoint do eksportu raportu do PDF
        Generuje kompletny raport z opisem, analizami i wizualizacjami
        
        GET /analysis-reporting/reports/{id}/export_pdf/
        """
        pdf_path = ReportManager.generate_pdf_report(pk)
        
        if not pdf_path:
            return Response(
                {"error": "Nie można wygenerować PDF lub raport nie istnieje"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            from django.conf import settings
            from django.http import FileResponse
            import os
            
            # Usuń /media/ z ścieżki
            file_path = pdf_path.replace('/media/', '')
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            if not os.path.exists(full_path):
                return Response(
                    {"error": "Plik PDF nie istnieje"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response = FileResponse(open(full_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Błąd podczas pobierania pliku PDF: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """
        Endpoint do pobierania raportów użytkownika
        GET /analysis-reporting/reports/by_user/?user_id=123
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reports = ReportManager.find_report_by_user_id(int(user_id))
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)


class AnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet dla analiz"""
    queryset = Analysis.objects.prefetch_related('visualizations').all()
    serializer_class = AnalysisSerializer
    authentication_classes = []
    permission_classes = []


class VisualizationViewSet(viewsets.ModelViewSet):
    """ViewSet dla wizualizacji"""
    queryset = Visualization.objects.all()
    serializer_class = VisualizationSerializer
    authentication_classes = []
    permission_classes = []
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Endpoint do pobierania pliku wykresu
        GET /analysis-reporting/visualizations/{id}/download/
        """
        visualization = self.get_object()
        
        if not visualization.file_path:
            return Response(
                {"error": "Brak pliku do pobrania"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            from django.conf import settings
            from django.http import FileResponse
            import os
            
            # Usuń /media/ z ścieżki jeśli istnieje
            file_path = visualization.file_path.replace('/media/', '')
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            if not os.path.exists(full_path):
                return Response(
                    {"error": "Plik nie istnieje"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response = FileResponse(open(full_path, 'rb'), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(full_path)}"'
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Błąd podczas pobierania pliku: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReportCompareViewSet(viewsets.ModelViewSet):
    """ViewSet dla porównań raportów"""
    queryset = ReportCompare.objects.select_related(
        'report_one', 'report_two'
    ).all()
    serializer_class = ReportCompareSerializer
    authentication_classes = []
    permission_classes = []
    
    @action(detail=False, methods=['post'])
    def compare(self, request):
        """
        Endpoint do porównywania raportów
        POST /analysis-reporting/comparisons/compare/
        Body: {
            "report_one_id": "uuid",
            "report_two_id": "uuid"
        }
        """
        report_one_id = request.data.get('report_one_id')
        report_two_id = request.data.get('report_two_id')
        
        try:
            report_one = Report.objects.get(report_id=report_one_id)
            report_two = Report.objects.get(report_id=report_two_id)
            
            comparison = ReportManager.compare_reports(report_one, report_two)
            serializer = self.get_serializer(comparison)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Report.DoesNotExist:
            return Response(
                {"error": "One or both reports not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        """
        Endpoint do eksportu porównania do PDF
        Generuje raport PDF z metadanymi, statystykami i wizualizacją
        
        GET /analysis-reporting/comparisons/{id}/export_pdf/
        """
        pdf_path = ReportManager.generate_comparison_pdf(pk)
        
        if not pdf_path:
            return Response(
                {"error": "Nie można wygenerować PDF lub porównanie nie istnieje"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            from django.conf import settings
            from django.http import FileResponse
            import os
            
            # Usuń /media/ z ścieżki
            file_path = pdf_path.replace('/media/', '')
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            if not os.path.exists(full_path):
                return Response(
                    {"error": "Plik PDF nie istnieje"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            response = FileResponse(open(full_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="comparison_{pk}.pdf"'
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Błąd podczas pobierania pliku PDF: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )