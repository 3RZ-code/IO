from django.http import JsonResponse
from .models import SimDevice

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
