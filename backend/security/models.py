from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    ROLE = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('spectator', 'Spectator'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE, default='admin')
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    terms_accepted = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Code(models.Model):
    PURPOSE_CHOICES = [
        ('RESET_PASSWORD', 'Reset Password'),
        ('CREATE_GROUP', 'Create Group'),
        ('TWO_FACTOR', 'Two Factor Auth'),
        ('GROUP_INVITATION', 'Group Invitation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='RESET_PASSWORD')

    def __str__(self):
        return f"{self.user.username} - {self.code} ({self.purpose})"

class GroupInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey('auth.Group', on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    code = models.CharField(max_length=8, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_invitations')

    def __str__(self):
        return f"Invitation to {self.group.name} for {self.email}"
    
    class Meta:
        ordering = ['-created_at']
