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


class GenerationHistory(models.Model):

    timestamp = models.DateTimeField()
    location = models.CharField(max_length=100, default="Lodz")
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_speed_ms = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    cloudiness_pct = models.PositiveSmallIntegerField(default=0)
    solar_irradiance_wm2 = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    pv_generation_kw = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    wind_generation_kw = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_generation_kw = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    weather_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.location} {self.timestamp.isoformat()} -> {self.total_generation_kw} kW"


class BatteryState(models.Model):
    """
    Przechowuje stan pojedynczej baterii w kWh.
    current_charge_kwh nie może przekraczać max_capacity_kwh.
    last_randomized_date pozwala losować stan raz dziennie.
    """

    max_capacity_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=100)
    current_charge_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    last_randomized_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Battery {self.current_charge_kwh}/{self.max_capacity_kwh} kWh"


class BatteryLog(models.Model):
    """
    Historia stanów baterii.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    charge_kwh = models.DecimalField(max_digits=12, decimal_places=3)
    source = models.CharField(max_length=50, default="system")  # np. randomized/add/remove

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.timestamp.isoformat()} -> {self.charge_kwh} kWh ({self.source})"