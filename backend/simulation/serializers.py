from rest_framework import serializers
from .models import GenerationHistory, SimDevice, BatteryState, BatteryLog


class GenerationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationHistory
        fields = "__all__"


class SimDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimDevice
        fields = "__all__"


class BatteryStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryState
        fields = "__all__"


class BatteryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryLog
        fields = "__all__"

