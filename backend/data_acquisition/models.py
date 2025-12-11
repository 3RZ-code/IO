from django.db import models

class DeviceReading(models.Model):
    timestamp = models.DateTimeField()
    device_id = models.CharField(max_length=50)
    device_type = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    metric = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    signal_dbm = models.IntegerField(default=0)
    status = models.BooleanField()
    name = models.CharField(max_length=100, default="Unknown Device")
    priority = models.IntegerField(default=2)  # 0 - high, 1 - medium, 2 - low

    def __str__(self):
        return f"{self.device_id} - {self.metric} @ {self.timestamp}"
    


    
