from django.contrib import admin
from .models import DeviceReading

@admin.register(DeviceReading)
class MyModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "timestamp",
        "device_id",
        "location",
        "metric",
        "value",
        "unit",
        "signal_dbm",
        "status",
    )
    list_filter = (
        "device_type", 
        "location", 
        "metric", 
        "status",
        ("timestamp", admin.DateFieldListFilter)
        )
    search_fields = ("device_id", "metric", "location")
