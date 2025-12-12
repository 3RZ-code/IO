from rest_framework import serializers
from communication.models import Schedule
from data_acquisition.models import Device


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer dla harmonogramu urządzeń"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_type = serializers.CharField(source='device.device_type', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'schedule_id',
            'device',
            'device_name',
            'device_type',
            'user_id',
            'start_date',
            'finish_date',
            'working_period',
            'working_status'
        ]
        read_only_fields = ['schedule_id']
    
    def validate(self, data):
        """
        Walidacja że start_date <= finish_date
        """
        start_date = data.get('start_date')
        finish_date = data.get('finish_date')
        
        if start_date and finish_date:
            if start_date > finish_date:
                raise serializers.ValidationError({
                    'finish_date': 'Data zakończenia musi być późniejsza lub równa dacie rozpoczęcia.'
                })
        
        return data


class ScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer do tworzenia harmonogramów"""
    
    class Meta:
        model = Schedule
        fields = [
            'device',
            'user_id',
            'start_date',
            'finish_date',
            'working_period',
            'working_status'
        ]
    
    def validate(self, data):
        """
        Walidacja że start_date <= finish_date
        """
        start_date = data.get('start_date')
        finish_date = data.get('finish_date')
        
        if start_date and finish_date:
            if start_date > finish_date:
                raise serializers.ValidationError({
                    'finish_date': 'Data zakończenia musi być późniejsza lub równa dacie rozpoczęcia.'
                })
        
        return data


class ScheduleUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer do aktualizacji statusu harmonogramu"""
    
    class Meta:
        model = Schedule
        fields = ['working_status']
