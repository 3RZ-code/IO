import csv
import os
from django.db import migrations

def fill_sim_devices(apps, schema_editor):
    SimDevice = apps.get_model('simulation', 'SimDevice')

    if SimDevice.objects.exists():
        print("\nSimDevice not empty, seeding skipped.")
        return

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'statics',
        'simulation_devices.csv'
    )
    if not os.path.exists(file_path):
        print(f"\nSeed CSV not found: {file_path}")
        return

    to_create = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            to_create.append(SimDevice(
                device_id=row['device_id'],
                type_code=row['type_code'],
                name=row['name'],
                status=row['status'],
                power_kw=(row['power_kw'] or None),
                pv_kwp=(row['pv_kwp'] or None),
                wind_rated_kw=(row['wind_rated_kw'] or None),
                hp_t_in_set_c=(row['hp_t_in_set_c'] or None),
                note=row.get('note') or ''
            ))

    if to_create:
        SimDevice.objects.bulk_create(to_create)
        print(f"SimDevice seeded from {file_path} ({len(to_create)} rows).")
