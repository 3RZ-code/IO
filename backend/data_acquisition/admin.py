from django.contrib import admin
from .models import DeviceReading, Device 

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id","device_id", "name", "device_type", "location", "is_active")
    list_filter = ("device_type", "location", "is_active")
    search_fields = ("device_id", "name", "location")


@admin.register(DeviceReading)
class MyModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "timestamp",
        "device",  
        "device_type",
        "location",
        "metric",
        "value",
        "unit",
        "signal_dbm",
        "status",
    )
    list_filter = (
        "device__device_type", 
        "location", 
        "metric", 
        "status",
        ("timestamp", admin.DateFieldListFilter)
        )
    search_fields = (
        "device__device_id", 
        "metric", 
        "location"
    )
    
    list_select_related = ('device',)