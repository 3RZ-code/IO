"""
Django Signals dla modułu alarm_alert.
Automatyczne tworzenie powiadomień w odpowiedzi na zmiany w alertach.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from alarm_alert.models import Alert, Notification
import pytz
from datetime import datetime


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
def create_notification_on_confirmation(sender, instance, created, **kwargs):
    pass  
