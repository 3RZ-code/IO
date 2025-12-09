from django.contrib import admin
from .models import Report, ReportCriteria, Analysis, Visualization, ReportCompare


@admin.register(ReportCriteria)
class ReportCriteriaAdmin(admin.ModelAdmin):
    list_display = ['report_criteria_id', 'location', 'report_frequency', 'date_created_from', 'date_created_to', 'device_type']
    list_filter = ['report_frequency', 'device_type', 'location']
    search_fields = ['location', 'device_type']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'created_by_id', 'created_timestamp', 'report_criteria']
    list_filter = ['created_timestamp']
    search_fields = ['report_description']
    readonly_fields = ['report_id', 'created_timestamp']


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['analysis_id', 'analysis_type', 'analysis_title', 'generate_chart', 'report']
    list_filter = ['analysis_type', 'generate_chart']
    search_fields = ['analysis_title', 'analysis_summary']
    readonly_fields = ['analysis_id']


@admin.register(Visualization)
class VisualizationAdmin(admin.ModelAdmin):
    list_display = ['visualization_id', 'chart_title', 'analysis']
    search_fields = ['chart_title']
    readonly_fields = ['visualization_id']


@admin.register(ReportCompare)
class ReportCompareAdmin(admin.ModelAdmin):
    list_display = ['report_compare_id', 'created_by_id', 'created_timestamp', 'report_one', 'report_two']
    readonly_fields = ['report_compare_id', 'created_timestamp']
    search_fields = ['compare_description']