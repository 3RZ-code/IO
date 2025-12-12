from rest_framework import serializers
from .models import Alert, Notification, NotificationPreferences
from security.models import User


class AlertSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'alert_id', 'user', 'user_email', 'user_username',
            'title', 'description', 'severity', 'status',
            'category', 'source', 'created_at', 'is_muted'
        ]
        read_only_fields = ['alert_id', 'created_at']

    def create(self, validated_data):
        alert = Alert.objects.create(**validated_data)
        return alert.createAlert()


class NotificationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'notification_id', 'user', 'user_email', 'user_username',
            'alert', 'alert_title', 'message', 'sent_at', 'is_read'
        ]
        read_only_fields = ['notification_id', 'sent_at']

    def create(self, validated_data):
        notification = Notification.objects.create(**validated_data)
        return notification.sendNotification()


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = NotificationPreferences
        fields = [
            'preference_id', 'user', 'user_email', 'user_username',
            'quiet_hours_start', 'quiet_hours_end', 'is_active'
        ]
        read_only_fields = ['preference_id']

    def update(self, instance, validated_data):
        quiet_hours_start = validated_data.get('quiet_hours_start')
        quiet_hours_end = validated_data.get('quiet_hours_end')
        
        if quiet_hours_start and quiet_hours_end:
            return instance.setQuietHours(quiet_hours_start, quiet_hours_end)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
