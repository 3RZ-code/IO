from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    device_id = models.IntegerField() 
    user_id = models.TextField()
    start_date = models.DateField()
    finish_date = models.DateField()
    working_period = models.TimeField()
    power_consumption = models.FloatField()
    working_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Schedule for Device ID {self.device_id} ({self.start_date} to {self.finish_date})"
