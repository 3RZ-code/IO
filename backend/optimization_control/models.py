from django.db import models

# Create your models here.
class Device(models.Model):
    device_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    power = models.FloatField()
    worktime = models.IntegerField()
    current_hours = models.CharField(max_length=10)
    priority = models.IntegerField()
    status = models.BooleanField(default=False)
    is_temp = models.BooleanField(default=False)

    def __str__(self):
        return self.name