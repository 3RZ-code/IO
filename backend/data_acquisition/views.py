from rest_framework import generics
from data_acquisition.models import DeviceReading
from .utils.serializers import DeviceReadingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.http import HttpResponse
from rest_framework.permissions import AllowAny


def index(request):
    return HttpResponse("Data acquisition module!")

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
        readings = DeviceReading.objects.all()
        if device_id:
            readings = readings.filter(device_id=device_id)
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