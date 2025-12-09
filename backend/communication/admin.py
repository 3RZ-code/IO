from django.contrib import admin
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule_id', 'device_id', 'user_id', 'start_date', 'finish_date', 'working_period', 'working_status')
    list_filter = ('working_status', 'start_date', 'finish_date')
    search_fields = ('device_id', 'user_id')