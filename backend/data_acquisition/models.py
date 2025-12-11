from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Device(models.Model):
    device_id = models.IntegerField(primary_key=True, db_index=True, help_text="Unikalny identyfikator urządzenia")
    name = models.CharField(max_length=100, blank=True, help_text="Przyjazna dla użytkownika nazwa")
    device_type = models.CharField(max_length=50, db_index=True)
    location = models.CharField(max_length=200, blank=True, help_text="Główna lokalizacja urządzenia")
    is_active = models.BooleanField(default=True, help_text="Czy urządzenie jest aktywne")
    priority = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)], help_text="Priorytet urządzenia (0-2)")

    class Meta:
        ordering = ['name', 'device_id']

    def __str__(self):
        return f"{self.name} ({self.device_id})"

class DeviceReading(models.Model):

    device = models.ForeignKey(
        Device, 
        on_delete=models.CASCADE,  
        related_name="readings",   
        help_text="Urządzenie, z którego pochodzi ten odczyt"
    )
    timestamp = models.DateTimeField()
    device_type = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    metric = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    signal_dbm = models.IntegerField(default=0)
    status = models.BooleanField(default=True, help_text="Status urządzenia (True/False")

    def __str__(self):
        return f"{self.device.device_id} - {self.metric} @ {self.timestamp}"