from django.http import JsonResponse
from .models import SimDevice
from .logic import SimulationLogic

def get_all_devices(request):
    data = list(SimDevice.objects.values(
        "device_id",
        "type_code",
        "name",
        "status",
        "power_kw",
        "pv_kwp",
        "wind_rated_kw",
        "hp_t_in_set_c",
        "note",
    ).order_by("device_id"))
    return JsonResponse(data, safe=False)

def trigger_simulation(request):
    """
    /simulation/run?sun=20&wind=50 (Tryb Syntetyczny)
    lub po prostu /simulation/run (Tryb Live - pobierze z weather.py)
    """
    sun = request.GET.get('sun')
    wind = request.GET.get('wind')
    temp = request.GET.get('temp')

    manual_data = None

    # Jeśli podano parametry w URL, tworzymy sztuczną pogodę
    if sun is not None or wind is not None:
        manual_data = {
            'sun': float(sun) if sun else 0,
            'wind': float(wind) if wind else 0,
            'temp': float(temp) if temp else 20
        }

    # Uruchamiamy logikę
    result = SimulationLogic.run_simulation(manual_weather=manual_data)

    return JsonResponse(result)