"""
Moduł monitorujący zdarzenia z różnych modułów i generujący alerty.
Automatycznie reaguje na zapisy danych z czujników i wykrycie anomalii w analizach.

Monitorowane moduły:
- data_acquisition: odczyty z czujników, status urządzeń
- analysis_reporting: wykrywanie anomalii, gotowość raportów
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from data_acquisition.models import Device, DeviceReading
from .models import Alert
import logging
import json

logger = logging.getLogger(__name__)

# Import modeli z analysis_reporting (dla signals)
try:
    from analysis_reporting.models import Report, Analysis
    ANALYSIS_REPORTING_AVAILABLE = True
except ImportError:
    ANALYSIS_REPORTING_AVAILABLE = False
    logger.warning("analysis_reporting models not available - signals disabled")


# ==================== KONFIGURACJA PROGÓW ====================

THRESHOLDS = {
    'temperature': {'min': 15, 'max': 30, 'unit': '°C'},
    'humidity': {'min': 30, 'max': 70, 'unit': '%'},
    'pressure': {'min': 900, 'max': 1100, 'unit': 'hPa'},
    'co2': {'min': 0, 'max': 1000, 'unit': 'ppm'},
    'voltage': {'min': 200, 'max': 250, 'unit': 'V'},
    'current': {'min': 0, 'max': 20, 'unit': 'A'},
    'power': {'min': 0, 'max': 5000, 'unit': 'W'},
}

# Minimalna siła sygnału (dBm)
MIN_SIGNAL_STRENGTH = -90  # poniżej tego = słaby sygnał


# ==================== MONITOROWANIE ODCZYTÓW ====================

@receiver(post_save, sender=DeviceReading)
def monitor_device_reading(sender, instance, created, **kwargs):
    """
    Automatycznie analizuje każdy nowy odczyt z czujnika.
    Generuje alerty dla:
    - Wartości poza zakresem
    - Słabego sygnału
    - Statusu urządzenia = False
    """
    if not created:
        return  
    
    reading = instance
    
    # 1. Sprawdź status urządzenia
    if not reading.status:
        create_alert_if_not_exists(
            title=f"Device Offline: {reading.device.name}",
            description=f"Device {reading.device.name} (ID: {reading.device.device_id}) reported offline status",
            severity='CRITICAL',
            category='device',
            source=f'device_{reading.device.device_id}'
        )
        logger.warning(f"Device {reading.device.device_id} is offline")
    
    # 2. Sprawdź siłę sygnału
    if reading.signal_dbm < MIN_SIGNAL_STRENGTH:
        create_alert_if_not_exists(
            title=f"Weak Signal: {reading.device.name}",
            description=f"Device {reading.device.name} has weak signal: {reading.signal_dbm} dBm (threshold: {MIN_SIGNAL_STRENGTH} dBm)",
            severity='WARNING',
            category='communication',
            source=f'device_{reading.device.device_id}'
        )
        logger.warning(f"Weak signal from device {reading.device.device_id}: {reading.signal_dbm} dBm")
    
    # 3. Sprawdź wartości metryk
    metric_lower = reading.metric.lower()
    if metric_lower in THRESHOLDS:
        threshold = THRESHOLDS[metric_lower]
        
        if reading.value < threshold['min']:
            create_alert_if_not_exists(
                title=f"Low {reading.metric}: {reading.device.name}",
                description=f"{reading.metric} is below threshold: {reading.value} {threshold['unit']} < {threshold['min']} {threshold['unit']}",
                severity='WARNING',
                category='sensor',
                source=f'device_{reading.device.device_id}'
            )
            logger.warning(f"Low {reading.metric} from device {reading.device.device_id}: {reading.value}")
        
        elif reading.value > threshold['max']:
            create_alert_if_not_exists(
                title=f"High {reading.metric}: {reading.device.name}",
                description=f"{reading.metric} is above threshold: {reading.value} {threshold['unit']} > {threshold['max']} {threshold['unit']}",
                severity='CRITICAL' if metric_lower in ['temperature', 'co2'] else 'WARNING',
                category='sensor',
                source=f'device_{reading.device.device_id}'
            )
            logger.warning(f"High {reading.metric} from device {reading.device.device_id}: {reading.value}")


@receiver(pre_save, sender=Device)
def monitor_device_status_change(sender, instance, **kwargs):
    """
    Monitoruje zmiany statusu urządzeń (is_active).
    Generuje alert gdy urządzenie staje się nieaktywne.
    Severity zależy od priorytetu urządzenia:
    - priority 0 (niski) → INFO
    - priority 1 (średni) → WARNING
    - priority 2 (wysoki) → CRITICAL
    """
    if instance.pk:  # Tylko dla istniejących urządzeń
        try:
            old_device = Device.objects.get(pk=instance.pk)
            
            # Sprawdź czy status się zmienił z aktywnego na nieaktywny
            if old_device.is_active and not instance.is_active:
                # Określ severity na podstawie priorytetu urządzenia
                severity_map = {
                    0: 'INFO',      # Niski priorytet
                    1: 'WARNING',   # Średni priorytet
                    2: 'CRITICAL'   # Wysoki priorytet
                }
                severity = severity_map.get(instance.priority, 'WARNING')
                
                create_alert_if_not_exists(
                    title=f"Device Deactivated: {instance.name}",
                    description=f"Device {instance.name} (ID: {instance.device_id}) has been deactivated (priority: {instance.priority})",
                    severity=severity,
                    category='device',
                    source=f'device_{instance.device_id}'
                )
                logger.info(f"Device {instance.device_id} deactivated (priority: {instance.priority}, severity: {severity})")
        except Device.DoesNotExist:
            pass


# ==================== MONITOROWANIE ANALYSIS & REPORTING ====================

if ANALYSIS_REPORTING_AVAILABLE:
    @receiver(post_save, sender=Analysis)
    def monitor_anomaly_detection(sender, instance, created, **kwargs):
        """
        Monitoruje wykrycie anomalii w analizach raportów.
        
        Generuje alert gdy:
        - Analiza typu ANOMALY została utworzona
        - has_anomaly = True (wykryto anomalie)
        
        Severity zależy od liczby wykrytych anomalii:
        - 1-3 anomalie → WARNING
        - 4-10 anomalii → WARNING (zwiększona uwaga)
        - 11+ anomalii → CRITICAL (poważny problem)
        """
        if not created:
            return
        
        # Tylko dla analiz ANOMALY z wykrytymi anomaliami
        if instance.analysis_type != 'ANOMALY' or not instance.has_anomaly:
            return
        
        # Parsuj analysis_summary (JSON) aby policzyć anomalie
        try:
            summary_data = json.loads(instance.analysis_summary) if isinstance(instance.analysis_summary, str) else instance.analysis_summary
            anomaly_count = summary_data.get('anomaly_count', 0)
            
            if anomaly_count == 0:
                return  # Brak anomalii, nie twórz alertu
            
        except (json.JSONDecodeError, AttributeError, TypeError):
            anomaly_count = 1
        
        # Określ severity na podstawie liczby anomalii
        if anomaly_count >= 11:
            severity = 'CRITICAL'
            severity_desc = 'critical level'
        elif anomaly_count >= 4:
            severity = 'WARNING'
            severity_desc = 'elevated level'
        else:
            severity = 'WARNING'
            severity_desc = 'moderate level'
        
        # Pobierz właściciela raportu
        from security.models import User
        report_owner = None
        if instance.report and instance.report.created_by_id:
            try:
                report_owner = User.objects.get(id=instance.report.created_by_id)
            except User.DoesNotExist:
                pass
        
        # Pobierz okres czasu z raportu
        report_period = ""
        if instance.report and instance.report.report_criteria:
            criteria = instance.report.report_criteria
            report_period = f" ({criteria.date_created_from} to {criteria.date_created_to})"
        
        create_alert_if_not_exists(
            title=f"Anomalies Detected: {instance.analysis_title}",
            description=f"{anomaly_count} anomalies detected at {severity_desc} in report analysis{report_period}. {instance.analysis_title}",
            severity=severity,
            category='analysis',
            source=f'analysis_{instance.analysis_id}',
            user=report_owner  # Przypisz do właściciela raportu
        )
        logger.warning(f"Anomaly alert created: {anomaly_count} anomalies detected (severity: {severity})")


if ANALYSIS_REPORTING_AVAILABLE:
    @receiver(post_save, sender=Report)
    def notify_report_ready(sender, instance, created, **kwargs):
        """
        Powiadamia użytkownika gdy raport został wygenerowany.
        
        Tworzy alert INFO informujący o dostępności nowego raportu.
        Alert przypisany jest do właściciela raportu (created_by_id).
        """
        
        if not created:
            return
        
        # Pobierz właściciela raportu
        from security.models import User
        report_owner = None
        if instance.created_by_id:
            try:
                report_owner = User.objects.get(id=instance.created_by_id)
            except User.DoesNotExist:
                logger.warning(f"Report owner not found: user_id={instance.created_by_id}")
                return
        
        # Pobierz szczegóły raportu
        report_period = "unknown period"
        location_info = ""
        
        if instance.report_criteria:
            criteria = instance.report_criteria
            if criteria.date_created_from and criteria.date_created_to:
                report_period = f"{criteria.date_created_from} to {criteria.date_created_to}"
            if criteria.location:
                location_info = f" for location '{criteria.location}'"
        
        # Policz analizy
        analyses_count = instance.analyses.count()
        
        create_alert_if_not_exists(
            title=f"Report Ready: {report_period}",
            description=f"Your report{location_info} has been generated with {analyses_count} analyses. Report ID: {instance.report_id}",
            severity='INFO',
            category='report',
            source=f'report_{instance.report_id}',
            user=report_owner  # Przypisz do właściciela raportu
        )
        logger.info(f"Report ready notification created for user {report_owner.username if report_owner else 'unknown'}")
else:
    logger.warning("analysis_reporting not available - Report/Analysis signals not registered")


# ==================== FUNKCJE POMOCNICZE (ROZSZERZONE) ====================

def create_alert_if_not_exists(title, description, severity, category, source, user=None):
    """
    Tworzy alert tylko jeśli podobny alert nie istnieje już dla tego źródła.
    Zapobiega duplikatom alertów.
    """
    # Sprawdź czy istnieje już aktywny alert dla tego źródła i kategorii
    recent_time = timezone.now() - timedelta(hours=1)
    
    existing_alert = Alert.objects.filter(
        category=category,
        source=source,
        status__in=['NEW', 'CONFIRMED'],
        created_at__gte=recent_time
    ).first()
    
    if existing_alert:
        logger.debug(f"Alert already exists for {source}, skipping creation")
        return None
    
    # Utwórz nowy alert
    alert = Alert.objects.create(
        title=title,
        description=description,
        severity=severity,
        category=category,
        source=source,
        user=user  # Może być None dla alertów systemowych
    )
    
    logger.info(f"Created alert: {title} (severity: {severity}, user: {user.username if user else 'system'})")
    return alert
