from rest_framework import serializers
from analysis_reporting.models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
            model = Report
            fields = [
                'id', 
                'created_by_id', 
                'created_timestamp', 
                'report_type', 
                'report_frequency', 
                'date_from', 
                'date_to'
            ]
            read_only_fields = ['created_timestamp']