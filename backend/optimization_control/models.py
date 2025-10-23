from django.db import models

# Create your models here.
class Device(models.Model):
    name = models.CharField(max_length=100)
    power = models.FloatField()
    worktime = models.IntegerField()
    current_cost = models.FloatField()
    priority = models.IntegerField()
    
    def __str__(self):
        return self.name