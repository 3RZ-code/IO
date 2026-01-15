from django.apps import AppConfig


class AlarmAlertConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alarm_alert'
    
    def ready(self):
        import alarm_alert.signals
        import alarm_alert.monitoring  # Ładuje sygnały monitorujące data_acquisition
