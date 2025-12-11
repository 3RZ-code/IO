from django.apps import AppConfig


class AlarmAlertConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alarm_alert'
    
    def ready(self):
        """
        Metoda wywoływana gdy aplikacja jest gotowa.
        Rejestrujemy tutaj Django signals.
        """
        import alarm_alert.signals
