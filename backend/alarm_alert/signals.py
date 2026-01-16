"""
Django Signals dla modułu alarm_alert.
Automatyczne tworzenie powiadomień w odpowiedzi na zmiany w alertach.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from alarm_alert.models import Alert, Notification, NotificationPreferences
from security.models import User
import pytz
import logging

logger = logging.getLogger(__name__)


# Częstotliwość wysyłania powiadomień (w minutach)
# Docker sprawdza co 60 sekund, ale:
# - CRITICAL: Wysyła powiadomienie co 15 minut
# - WARNING: Wysyła powiadomienie co 60 minut
# - INFO: Wysyła powiadomienie co 24h
NOTIFICATION_INTERVALS = {
    'CRITICAL': 15,     # Co 15 minut
    'WARNING': 60,      # Co godzinę
    'INFO': 1440,       # Co 24h
}


@receiver(pre_save, sender=Alert)
def detect_alert_status_change(sender, instance, **kwargs):
    """
    Zapisuje stary status alertu PRZED zapisem.
    Dzięki temu w post_save możemy porównać starą i nową wartość.
    """
    if instance.pk:  
        try:
            old_alert = Alert.objects.get(pk=instance.pk)
            instance._old_status = old_alert.status
        except Alert.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None 


@receiver(post_save, sender=Alert)
def handle_alert_notifications(sender, instance, created, **kwargs):
    """
    Automatycznie tworzy powiadomienia dla alertów.
    
    ZASADY:
    1. Nowy alert (created=True) z statusem NEW → wysyłaj powiadomienia
    2. Alert zmienił status NA NEW → wysyłaj powiadomienia
    3. Alert ma status CONFIRMED/CLOSED/MUTED → NIE wysyłaj
    4. Częstotliwość zależna od severity (zapobiega spamowi)
    """
    
    # Tylko dla statusu NEW
    if instance.status != 'NEW':
        return
    
    # Sprawdź czy to nowy alert lub zmiana statusu na NEW
    if created:
        send_notifications_for_alert(instance, reason="new_alert")
    elif hasattr(instance, '_old_status') and instance._old_status != 'NEW':
        send_notifications_for_alert(instance, reason="status_changed_to_new")


def send_notifications_for_alert(alert, reason="new_alert"):
    """
    Wysyła powiadomienia o alercie do odpowiednich użytkowników.
    
    Uwzględnia:
    - Preferencje użytkownika (is_active, quiet_hours)
    - Role (admini dostają wszystko, user tylko swoje)
    """
    
    # Zbierz odbiorców
    recipients = set()
    
    # 1. Jeśli alert przypisany do użytkownika - dodaj go
    if alert.user:
        recipients.add(alert.user)
    
    # 2. CRITICAL - admini zawsze dostają
    if alert.severity == 'CRITICAL':
        admins = User.objects.filter(role='admin')
        for admin in admins:
            recipients.add(admin)
        # Jeśli nie ma właściciela - tylko admini (nie spamuj userów)
    
    # 3. WARNING bez właściciela - admini + wszyscy userzy
    elif alert.severity == 'WARNING' and not alert.user:
        all_users = User.objects.all()  # Wszyscy (admini + userzy)
        for user in all_users:
            recipients.add(user)
    
    # 4. INFO bez właściciela - admini + wszyscy userzy (np. raporty systemowe)
    elif alert.severity == 'INFO' and not alert.user:
        all_users = User.objects.all()  # Wszyscy (admini + userzy)
        for user in all_users:
            recipients.add(user)
    
    # 5. INFO/WARNING z właścicielem - tylko właściciel
    
    if not recipients:
        return
    
    # Wysyłaj powiadomienia z uwzględnieniem preferencji
    local_tz = pytz.timezone('Europe/Warsaw')
    current_time = timezone.now().astimezone(local_tz).time()
    
    notifications_sent = 0
    for user in recipients:
        # Sprawdź preferencje użytkownika
        preferences = NotificationPreferences.objects.filter(user=user).first()
        
        # Czy powiadomienia są włączone?
        if preferences and not preferences.is_active:
            continue
        
        # Czy nie jesteśmy w quiet hours?
        if preferences and preferences.quiet_hours_start and preferences.quiet_hours_end:
            if preferences.quiet_hours_start <= current_time <= preferences.quiet_hours_end:
                continue
        
        # Utwórz powiadomienie
        Notification.objects.create(
            user=user,
            alert=alert,
            message=f"[{alert.severity}] {alert.title}: {alert.description}"
        )
        notifications_sent += 1


@receiver(post_save, sender=Alert)  
def handle_confirmation_notifications(sender, instance, created, **kwargs):
    """
    Wysyła powiadomienia gdy alert zostanie POTWIERDZONY.
    Tylko jeśli status zmienił się na CONFIRMED.
    """
    if created:
        return  # Nie dotyczy nowych alertów
    
    old_status = getattr(instance, '_old_status', None)
    
    # Jeśli zmieniono status na CONFIRMED
    if old_status and old_status != 'CONFIRMED' and instance.status == 'CONFIRMED':
        logger.info(f"Alert potwierdzony: {instance.title}")
        send_confirmation_notifications(instance)


def send_confirmation_notifications(alert):
    """
    Powiadamia administratorów i właściciela o potwierdzeniu alertu.
    Uwzględnia preferencje użytkownika (is_active, quiet_hours).
    """
    recipients = set()
    
    # Dodaj adminów
    admins = User.objects.filter(role='admin')
    for admin in admins:
        recipients.add(admin)
    
    # Dodaj właściciela alertu (jeśli istnieje)
    if alert.user:
        recipients.add(alert.user)
    
    # Wyślij powiadomienia z uwzględnieniem preferencji
    local_tz = pytz.timezone('Europe/Warsaw')
    current_time = timezone.now().astimezone(local_tz).time()
    
    notifications_sent = 0
    for user in recipients:
        # Sprawdź preferencje użytkownika
        preferences = NotificationPreferences.objects.filter(user=user).first()
        
        # Czy powiadomienia są włączone?
        if preferences and not preferences.is_active:
            continue
        
        # Czy nie jesteśmy w quiet hours?
        if preferences and preferences.quiet_hours_start and preferences.quiet_hours_end:
            if preferences.quiet_hours_start <= current_time <= preferences.quiet_hours_end:
                continue
        
        Notification.objects.create(
            user=user,
            alert=alert,
            message=f"Alert potwierdzony przez {alert.confirmed_by.username if alert.confirmed_by else 'system'}: {alert.title}"
        )
        notifications_sent += 1
    
    logger.info(f"Wysłano {notifications_sent}/{len(recipients)} powiadomień o potwierdzeniu alertu: {alert.title}")  
