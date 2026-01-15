"""
Management command: send_periodic_notifications

Wysyła powtarzające się powiadomienia dla alertów ze statusem NEW.

LOGIKA:
- Docker uruchamia command co 60 sekund (wymóg: wykrycie <60s)
- Sprawdza wszystkie alerty ze statusem NEW
- Dla każdego alertu sprawdza kiedy ostatnio wysłano powiadomienie
- Jeśli minął odpowiedni czas (severity-dependent) → wysyła nowe powiadomienie
- CRITICAL: Co 15 minut (wykrycie <60s, ale powiadomienie co 15min)
- WARNING: Co 60 minut (1h)
- INFO: Co 1440 minut (24h)

URUCHOMIENIE:
- Manualnie: python manage.py send_periodic_notifications
- Docker periodic container (zalecane, co 60s)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from alarm_alert.models import Alert, Notification
from alarm_alert.signals import send_notifications_for_alert, NOTIFICATION_INTERVALS
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Wysyła powtarzające się powiadomienia dla alertów NEW według interwałów severity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Tylko pokaż co zostałoby zrobione, bez wysyłania',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Znajdź wszystkie alerty ze statusem NEW
        new_alerts = Alert.objects.filter(status='NEW').select_related('user')
        
        if new_alerts.count() == 0:
            return
        
        sent_count = 0
        skipped_count = 0
        
        for alert in new_alerts:
            interval = NOTIFICATION_INTERVALS.get(alert.severity, 60)
            
            # Sprawdź kiedy ostatnio wysłano powiadomienie DLA TEGO ALERTU
            last_notification = Notification.objects.filter(
                alert=alert
            ).order_by('-sent_at').first()
            
            # Jeśli nigdy nie wysłano - wyślij teraz
            if not last_notification:
                if not dry_run:
                    send_notifications_for_alert(alert)
                sent_count += 1
                continue
            
            # Sprawdź czy minął wymagany czas od ostatniego powiadomienia
            time_since_last = timezone.now() - last_notification.sent_at
            minutes_since_last = time_since_last.total_seconds() / 60
            
            if minutes_since_last >= interval:
                if not dry_run:
                    send_notifications_for_alert(alert)
                sent_count += 1
            else:
                skipped_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Wysłano: {sent_count}, Pominięto: {skipped_count}')
            )
