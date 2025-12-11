from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("simulation", "0002_seed_simdevices"),
    ]

    operations = [
        migrations.CreateModel(
            name="GenerationHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField()),
                ("location", models.CharField(default="Lodz", max_length=100)),
                ("temperature_c", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("wind_speed_ms", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("cloudiness_pct", models.PositiveSmallIntegerField(default=0)),
                ("solar_irradiance_wm2", models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ("pv_generation_kw", models.DecimalField(decimal_places=3, default=0, max_digits=12)),
                ("wind_generation_kw", models.DecimalField(decimal_places=3, default=0, max_digits=12)),
                ("total_generation_kw", models.DecimalField(decimal_places=3, default=0, max_digits=12)),
                ("weather_payload", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-timestamp",),
            },
        ),
    ]

