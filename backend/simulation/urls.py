from django.urls import path
from .views import get_all_devices

urlpatterns = [
    path("devices/", get_all_devices),  # GET /simulation/devices/
]
