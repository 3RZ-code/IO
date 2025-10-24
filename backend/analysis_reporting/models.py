from django.db import models
from django.contrib.auth.models import User  # Import standardowego modelu User
from django.utils.translation import gettext_lazy as _

class Report(models.Model):
    class ReportType(models.TextChoices):
        # analiza kosztów, szczytowe obciążenie, produkcja OZE 
        COST_ANALYSIS = 'COST', _('Cost Analysis')
        PEAK_LOAD = 'PEAK', _('Peak Load')
        OZE_PRODUCTION = 'OZE', _('OZE Production')

    class ReportFrequency(models.TextChoices):
        DAILY = 'DAILY', _('Daily')
        WEEKLY = 'WEEKLY', _('Weekly')
        MONTHLY = 'MONTHLY', _('Monthly')

    # created_by_id = models.ForeignKey(
    #     User,  
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name=_("Created by")
    # )
    created_by_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Created by")
    )
    
    created_timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Created at")
    )

    report_type = models.CharField(
        max_length=10,
        choices=ReportType.choices,
        verbose_name=_("Report Type (Content)")
    )
    
    report_frequency = models.CharField(
        max_length=10,
        choices=ReportFrequency.choices,
        default=ReportFrequency.MONTHLY,
        verbose_name=_("Report Frequency")
    )

    date_from = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Date from")
    )
    
    date_to = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Date to")
    )

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ['-created_timestamp']

    def __str__(self):
        return f"{self.get_report_type_display()} ({self.get_report_frequency_display()})"