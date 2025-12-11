from rest_framework import serializers
from analysis_reporting.models import (
    Report, 
    ReportCriteria, 
    Analysis, 
    Visualization, 
    ReportCompare
)


class ReportCriteriaSerializer(serializers.ModelSerializer):
    """Serializer dla kryteriów raportu"""
    
    class Meta:
        model = ReportCriteria
        fields = [
            'report_criteria_id',
            'location',
            'report_frequency',
            'date_created_from',
            'date_created_to',
            'device_type'
        ]
        read_only_fields = ['report_criteria_id']
    
    def validate(self, data):
        """
        Walidacja że date_created_from < date_created_to
        """
        date_from = data.get('date_created_from')
        date_to = data.get('date_created_to')
        
        if date_from and date_to:
            if date_from > date_to:
                raise serializers.ValidationError({
                    'date_created_to': 'Data końcowa musi być późniejsza niż data początkowa.'
                })
        
        return data


class VisualizationSerializer(serializers.ModelSerializer):
    """Serializer dla wizualizacji"""
    
    class Meta:
        model = Visualization
        fields = [
            'visualization_id',
            'chart_title',
            'file_path',
            'analysis'
        ]
        read_only_fields = ['visualization_id']


class AnalysisSerializer(serializers.ModelSerializer):
    """Serializer dla analizy z zagnieżdżonymi wizualizacjami"""
    visualizations = VisualizationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'analysis_id',
            'analysis_type',
            'analysis_title',
            'analysis_summary',
            'generate_chart',
            'report',
            'visualizations'
        ]
        read_only_fields = ['analysis_id']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer dla raportu z zagnieżdżonymi analizami i kryteriami"""
    analyses = AnalysisSerializer(many=True, read_only=True)
    report_criteria = ReportCriteriaSerializer(read_only=True)
    report_criteria_id = serializers.PrimaryKeyRelatedField(
        queryset=ReportCriteria.objects.all(),
        source='report_criteria',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Report
        fields = [
            'report_id',
            'created_by_id',
            'created_timestamp',
            'report_criteria',
            'report_criteria_id',
            'data_for_analysis',
            'report_description',
            'analyses'
        ]
        read_only_fields = ['report_id', 'created_timestamp']


class ReportCompareSerializer(serializers.ModelSerializer):
    """Serializer dla porównania raportów"""
    report_one = ReportSerializer(read_only=True)
    report_two = ReportSerializer(read_only=True)
    report_one_id = serializers.PrimaryKeyRelatedField(
        queryset=Report.objects.all(),
        source='report_one',
        write_only=True
    )
    report_two_id = serializers.PrimaryKeyRelatedField(
        queryset=Report.objects.all(),
        source='report_two',
        write_only=True
    )
    
    class Meta:
        model = ReportCompare
        fields = [
            'report_compare_id',
            'created_by_id',
            'created_timestamp',
            'compare_description',
            'report_one',
            'report_two',
            'report_one_id',
            'report_two_id'
        ]
        read_only_fields = ['report_compare_id', 'created_timestamp']