from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from data_acquisition.utils.serializers import DeviceReadingSerializer
from data_acquisition.utils.device_reading import get_all_readings

def index(request):
    return HttpResponse("Data acquisition module!")

class DeviceReadingList(APIView):
    def get(self,request):
        readings = get_all_readings()
        serializer = DeviceReadingSerializer(readings, many=True)
        return Response(serializer.data)

