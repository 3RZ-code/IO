from django.contrib import admin
from .models import SimDevice

@admin.register(SimDevice)
class SimDeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id","type_code","name","status","power_kw")
    search_fields = ("device_id","name")
    list_filter = ("type_code","status")
