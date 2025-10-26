from django.db import models

class SimDevice(models.Model):
    class TypeCode(models.TextChoices):
        PV = 'pv', 'pv'
        WIND = 'wind', 'wind'
        HP = 'hp', 'hp'
        OTHER = 'other', 'other'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'active'
        INACTIVE = 'inactive', 'inactive'
        DISABLED = 'disabled', 'disabled'

    device_id = models.CharField(max_length=64, primary_key=True)
    type_code = models.CharField(max_length=10, choices=TypeCode.choices)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    power_kw = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    pv_kwp = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    wind_rated_kw = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    hp_t_in_set_c = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.device_id} ({self.type_code})"
