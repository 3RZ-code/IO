from django.contrib import admin
from .models import Alert, Notification, NotificationPreferences


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['alert_id', 'title', 'severity', 'status', 'user', 'category', 'created_at', 'is_muted']
    list_filter = ['severity', 'status', 'category', 'is_muted', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    readonly_fields = ['alert_id', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'user', 'message_preview', 'sent_at', 'is_read', 'alert']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['message', 'user__username', 'user__email']
    readonly_fields = ['notification_id', 'sent_at']
    date_hierarchy = 'sent_at'
    ordering = ['-sent_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'


@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ['preference_id', 'user', 'quiet_hours_start', 'quiet_hours_end', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['preference_id']

