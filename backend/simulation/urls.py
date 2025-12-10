from django.urls import path
from .views import get_all_devices, trigger_simulation

urlpatterns = [
    path("devices/", get_all_devices),  # GET /simulation/devices/
    path("run/", trigger_simulation),  # Uruchomienie symulacji (Live lub Demo)
]