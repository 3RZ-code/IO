from django.contrib import admin
from .models import DeviceReading

@admin.register(DeviceReading)
class MyModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "timestamp",
        "device_id",
        "device_type",
        "location",
        "metric",
        "value",
        "unit",
        "signal_dbm",
        "status",
        "name",
        "priority",
    )
    list_filter = ("device_type", "location", "metric", "status")
    search_fifleds = ("device_id", "metric", "location")
