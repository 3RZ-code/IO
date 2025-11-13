from rest_framework import generics
from data_acquisition.models import DeviceReading, Device
from .utils.serializers import DeviceReadingSerializer, DeviceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.http import HttpResponse
from rest_framework.permissions import AllowAny


def index(request):
    return HttpResponse("Data acquisition module!")


class DeviceListCreate(generics.ListCreateAPIView):

    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class DeviceDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class DeviceReadingListCreate(generics.ListCreateAPIView):
    queryset = DeviceReading.objects.all()
    serializer_class = DeviceReadingSerializer

class DeviceReadingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeviceReading.objects.all()
    serializer_class = DeviceReadingSerializer

class DeviceReadingFilter(APIView):
    permission_classes = [AllowAny] 
    def get(self, request):
        device_id = request.GET.get("device_id")
        location = request.GET.get("location")
        metric = request.GET.get("metric")
        timestamp = request.GET.get("timestamp") 
        start = request.GET.get("start")
        end = request.GET.get("end")
        readings = DeviceReading.objects.all().select_related('device') 
        
        if device_id:
            readings = readings.filter(device__device_id=device_id)
        
        if location:
            readings = readings.filter(location=location)
        if metric:
            readings = readings.filter(metric=metric)
        if timestamp:
            dt = parse_datetime(timestamp)
            if dt:
                readings = readings.filter(timestamp=dt)
        if start:
            dt_start = parse_datetime(start)
            if dt_start:
                readings = readings.filter(timestamp__gte=dt_start)
        if end:
            dt_end = parse_datetime(end)
            if dt_end:
                readings = readings.filter(timestamp__lte=dt_end)

        serializer = DeviceReadingSerializer(readings, many=True)
        return Response(serializer.data)