from rest_framework import serializers
from data_acquisition.models import DeviceReading

class DeviceReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceReading
        fields = "__all__"