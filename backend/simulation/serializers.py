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


class RunGenerationRangeSerializer(serializers.Serializer):
    """Serializer dla body requestu w /simulation/generation/run-range/"""
    start = serializers.CharField(
        required=True,
        help_text="Data rozpoczęcia w formacie YYYY-MM-DD lub YYYY-MM-DDTHH:MM:SS"
    )
    end = serializers.CharField(
        required=True,
        help_text="Data zakończenia w formacie YYYY-MM-DD lub YYYY-MM-DDTHH:MM:SS"
    )
    step_hours = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        help_text="Krok czasowy w godzinach (domyślnie 3)"
    )

