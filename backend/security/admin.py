from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Code

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'two_factor_enabled', 'is_staff')
    list_filter = ('role', 'two_factor_enabled', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Security Settings', {'fields': ('role', 'two_factor_enabled', 'google_id', 'birth_date')}),
        ('Agreements', {'fields': ('terms_accepted', 'privacy_policy_accepted')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
         ('Security Settings', {'fields': ('role', 'two_factor_enabled', 'email', 'first_name', 'last_name')}),
    )

class CodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'purpose', 'created_at')
    list_filter = ('purpose', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('created_at',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Code, CodeAdmin)
