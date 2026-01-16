from django.contrib import admin
from .models import SimDevice, GenerationHistory, BatteryState, BatteryLog

@admin.register(SimDevice)
class SimDeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id","type_code","name","status","power_kw")
    search_fields = ("device_id","name")
    list_filter = ("type_code","status")


@admin.register(GenerationHistory)
class GenerationHistoryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "location", "total_generation_kw", "pv_generation_kw", "wind_generation_kw", "cloudiness_pct")
    search_fields = ("location",)
    list_filter = ("location", "cloudiness_pct")


@admin.register(BatteryState)
class BatteryStateAdmin(admin.ModelAdmin):
    list_display = ("id", "current_charge_kwh", "max_capacity_kwh")
    search_fields = ("id",)


@admin.register(BatteryLog)
class BatteryLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "charge_kwh", "source")
    list_filter = ("source",)
