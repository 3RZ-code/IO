# Generated manually - zmiana device_id na ForeignKey do Device

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_acquisition', '0001_initial'),
        ('communication', '0002_seed_fill_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='device_id',
        ),
        migrations.AddField(
            model_name='schedule',
            name='device',
            field=models.ForeignKey(
                default=1,  # Tymczasowa wartość domyślna
                help_text='Urządzenie powiązane z harmonogramem',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='schedules',
                to='data_acquisition.device',
            ),
            preserve_default=False,
        ),
    ]
