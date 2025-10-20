from django.db import migrations
from simulation.utils.fill_data import fill_sim_devices

class Migration(migrations.Migration):

    dependencies = [
        ('simulation', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fill_sim_devices),
    ]
