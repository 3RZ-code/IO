from django.db import models
from django.contrib.auth.models import User  # Import standardowego modelu User
from django.utils.translation import gettext_lazy as _
import uuid


class ReportCriteria(models.Model):
    """
    Kryteria dla raportów - definiuje parametry filtrowania danych
    """
    class ReportFrequency(models.TextChoices):
        DAILY = 'DAILY', _('Daily')
        WEEKLY = 'WEEKLY', _('Weekly')
        MONTHLY = 'MONTHLY', _('Monthly')
        YEARLY = 'YEARLY', _('Yearly')
        CUSTOM = 'CUSTOM', _('Custom')

    report_criteria_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Location")
    )
    
    report_frequency = models.CharField(
        max_length=10,
        choices=ReportFrequency.choices,
        default=ReportFrequency.MONTHLY,
        verbose_name=_("Report Frequency")
    )
    
    date_created_from = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date from")
    )
    
    date_created_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date to")
    )
    
    device_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Device Type")
    )

    class Meta:
        verbose_name = _("Report Criteria")
        verbose_name_plural = _("Report Criteria")

    def __str__(self):
        return f"Criteria {self.report_criteria_id} - {self.get_report_frequency_display()}"

    def clean(self):
        """Walidacja modelu"""
        from django.core.exceptions import ValidationError
        
        if self.date_created_from and self.date_created_to:
            if self.date_created_from > self.date_created_to:
                raise ValidationError({
                    'date_created_to': 'Data końcowa musi być późniejsza niż data początkowa.'
                })
    
    def save(self, *args, **kwargs):
        """Nadpisanie save z walidacją"""
        self.clean()
        super().save(*args, **kwargs)

    def validate_type(self):
        """Walidacja kryteriów"""
        if not self.date_created_from or not self.date_created_to:
            return False
        return True


class Report(models.Model):
    """
    Główny model raportu
    Raport zawiera dane z określonego okresu czasu.
    Przy tworzeniu automatycznie generowane są analizy TRENDS i PEAK.
    Analiza ANOMALY tworzona jest na żądanie użytkownika.
    """

    report_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_by_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Created by")
    )
    
    created_timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Created at")
    )

    report_criteria = models.ForeignKey(
        ReportCriteria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name=_("Report Criteria")
    )
    
    data_for_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Data for Analysis")
    )
    
    report_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Report Description")
    )

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ['-created_timestamp']

    def __str__(self):
        period = ""
        if self.report_criteria:
            period = f"{self.report_criteria.date_created_from} - {self.report_criteria.date_created_to}"
        return f"Report {self.report_id} ({period})"

    def generate(self):
        """Generuje raport na podstawie kryteriów"""
        return True

    def identify_anomaly(self):
        """Identyfikuje anomalie w danych"""
        return False

    def load_sensor_data(self):
        """Ładuje dane z sensorów"""
        return True

    def export_analysis_data(self):
        """Eksportuje dane analityczne do JSON"""
        return self.data_for_analysis

    def create_visualization(self, analysis):
        """Tworzy wizualizację dla analizy"""
        return True


class Analysis(models.Model):
    """
    Analiza powiązana z raportem
    """
    class AnalysisType(models.TextChoices):
        TRENDS = 'TRENDS', _('Trends')
        PEAK = 'PEAK', _('Peak')
        ANOMALY = 'ANOMALY', _('Anomaly')

    analysis_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    analysis_type = models.CharField(
        max_length=20,
        choices=AnalysisType.choices,
        verbose_name=_("Analysis Type")
    )
    
    analysis_title = models.CharField(
        max_length=200,
        verbose_name=_("Analysis Title")
    )
    
    analysis_summary = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Analysis Summary")
    )
    
    generate_chart = models.BooleanField(
        default=False,
        verbose_name=_("Generate Chart")
    )
    
    has_anomaly = models.BooleanField(
        default=False,
        verbose_name=_("Has Anomaly Detected")
    )
    
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name=_("Report")
    )

    class Meta:
        verbose_name = _("Analysis")
        verbose_name_plural = _("Analyses")

    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.analysis_title}"

    def create_visualization(self):
        """Tworzy wizualizację dla tej analizy"""
        return True

    def get_analysis_summary(self):
        """Zwraca podsumowanie analizy"""
        return self.analysis_summary


class Visualization(models.Model):
    """
    Wizualizacja dla analizy
    """
    visualization_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    chart_title = models.CharField(
        max_length=200,
        verbose_name=_("Chart Title")
    )
    
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("File Path")
    )
    
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name='visualizations',
        verbose_name=_("Analysis")
    )

    class Meta:
        verbose_name = _("Visualization")
        verbose_name_plural = _("Visualizations")

    def __str__(self):
        return f"{self.chart_title} ({self.visualization_id})"

    def render_to_pdf(self, analysis):
        """Renderuje wizualizację do PDF"""
        return True

    def download_file(self):
        """Pobiera plik wizualizacji"""
        return None


class ReportCompare(models.Model):
    """
    Porównanie dwóch raportów
    """
    report_compare_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    created_by_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Created by")
    )
    
    created_timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at")
    )
    
    compare_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Compare Description")
    )
    
    report_one = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='comparisons_as_one',
        verbose_name=_("Report One")
    )
    
    report_two = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='comparisons_as_two',
        verbose_name=_("Report Two")
    )
    
    visualization_file = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Visualization File Path")
    )

    class Meta:
        verbose_name = _("Report Compare")
        verbose_name_plural = _("Report Comparisons")
        ordering = ['-created_timestamp']

    def __str__(self):
        return f"Compare {self.report_compare_id}"

    def compare(self):
        """Porównuje dwa raporty"""
        return True