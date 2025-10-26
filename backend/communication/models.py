from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Device(models.Model):
    device_id = models.AutoField(primary_key=True)
    device_name = models.TextField()
    device_type = models.TextField()
    zone = models.TextField()
    activated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.device_name} ({self.device_type})"

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user_id = models.TextField()
    start_date = models.DateField()
    finish_date = models.DateField()
    working_period = models.TimeField()
    power_consumption = models.FloatField()
    working_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Schedule for {self.device.device_name} ({self.start_date} to {self.finish_date})"
