from django.db import models
from security.models import User
import uuid


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('WARNING', 'Warning'),
        ('INFO', 'Info'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONFIRMED', 'Confirmed'),
        ('MUTED', 'Muted'),
        ('CLOSED', 'Closed'),
    ]
    
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='INFO')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    category = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_muted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['severity', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.title}"

    def createAlert(self):
        self.save()
        return self

    def confirmAlert(self):
        self.status = 'CONFIRMED'
        self.save()
        return self

    def muteAlert(self):
        self.is_muted = True
        self.status = 'MUTED'
        self.save()
        return self

    def deleteAlert(self):
        self.delete()


class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    alert = models.ForeignKey(Alert, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"

    def sendNotification(self):
        self.save()
        return self

    def markAsRead(self):
        self.is_read = True
        self.save()
        return self


class NotificationPreferences(models.Model):
    preference_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Preferences for {self.user.username}"

    def setQuietHours(self, start_time, end_time):
        self.quiet_hours_start = start_time
        self.quiet_hours_end = end_time
        self.save()
        return self
