from django.db import models


class Alert(models.Model):
    alarm_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True)
    device_id = models.IntegerField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100)

    category = models.CharField(
        max_length=30,
        choices=[
            ('system', 'System'),
            ('energy', 'Energia'),
            ('weather', 'Pogoda'),
            ('report', 'Raport'),
        ]
    )
    severity = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Informacyjny'),
            ('warning', 'Ostrzeżenie'),
            ('critical', 'Krytyczny'),
        ]
    )

    message = models.TextField()
    details = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Otwarty'),
            ('acknowledged', 'Potwierdzony'),
            ('resolved', 'Zamknięty'),
        ],
        default='open'
    )

    is_quiet_hours = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    visible_for = models.CharField(
        max_length=10,
        choices=[
            ('admin', 'Admin'),
            ('user', 'User'),
            ('both', 'Obaj'),
        ],
        default='both'
    )

    def __str__(self):
        return f"[{self.severity.upper()}] {self.message[:50]}"
