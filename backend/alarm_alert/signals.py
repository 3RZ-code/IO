"""
Django Signals dla modułu alarm_alert.
Automatyczne tworzenie powiadomień w odpowiedzi na zmiany w alertach.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from alarm_alert.models import Alert, Notification


@receiver(pre_save, sender=Alert)
def detect_alert_status_change(sender, instance, **kwargs):
    """
    Zapisuje stary status alertu PRZED zapisem.
    Dzięki temu w post_save możemy porównać starą i nową wartość.
    """
    if instance.pk:  # Tylko dla istniejących alertów
        try:
            old_alert = Alert.objects.get(pk=instance.pk)
            instance._old_status = old_alert.status
        except Alert.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None  # Nowy alert


@receiver(post_save, sender=Alert)
def create_notification_on_confirmation(sender, instance, created, **kwargs):
    """
    Tworzy powiadomienie gdy alert zostaje potwierdzony.
    
    Przypadek:
    - status zmieniony na 'CONFIRMED' → Powiadomienie dla użytkownika
    """
    # Pomiń nowe alerty
    if created:
        return
    
    # Sprawdź czy status się zmienił
    old_status = getattr(instance, '_old_status', None)
    if old_status is None or old_status == instance.status:
        return  # Brak zmiany statusu
    
    # Sprawdź czy alert został potwierdzony
    if instance.status == 'CONFIRMED':
        # Jeśli alert nie ma użytkownika, przypisz do pierwszego admina
        user = instance.user
        if user is None:
            from security.models import User
            user = User.objects.filter(role='admin').first()
            if user is None:
                user = User.objects.first()  # Fallback do pierwszego użytkownika
        
        # Utwórz powiadomienie (tylko jeśli znaleziono użytkownika)
        if user:
            Notification.objects.create(
                user=user,
                alert=instance,
                message=f"Alert '{instance.title}' został potwierdzony.",
                sent_at=timezone.now()
            )
