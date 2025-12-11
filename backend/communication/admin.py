from django.contrib import admin
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule_id', 'device_id', 'user_id', 'start_date', 'finish_date', 'working_status')
    list_filter = ('working_status', 'start_date', 'finish_date')
    search_fields = ('device_id', 'user_id')
    ordering = ('-start_date',)
    list_per_page = 20

    list_editable = ('working_status',)

    readonly_fields = ('schedule_id',)
    
    fieldsets = (
        ('Identyfikacja', {
            'fields': ('schedule_id', 'device_id', 'user_id')
        }),
        ('Harmonogram', {
            'fields': ('start_date', 'finish_date', 'working_period')
        }),
        ('Status', {
            'fields': ('working_status',)
        }),
    )
