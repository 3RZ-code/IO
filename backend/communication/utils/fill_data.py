import csv
import os
from datetime import datetime
from django.db import migrations

def fill_devices(apps, schema_editor):
    Device = apps.get_model('communication', 'Device')
    
    if Device.objects.exists():
        print("\nDevices table is not empty, filling aborted.")
        return

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'statics',
        'Device.csv'
    )

    if not os.path.exists(file_path):
        print(f"\nFile {file_path} does not exist. Aborting.")
        return

    devices_to_create = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                device_instance = Device(
                    device_id=int(row['device_id']),
                    device_name=row['device_name'],
                    device_type=row['device_type'],
                    zone=row['zone'],
                    activated=bool(int(row['activated']))
                )
                devices_to_create.append(device_instance)

        if devices_to_create:
            Device.objects.bulk_create(devices_to_create)
            print(f"\n{len(devices_to_create)} devices successfully loaded from {file_path}.")

    except Exception as e:
        print(f"\nError occurred while loading CSV file: {e}")

def fill_schedules(apps, schema_editor):
    Schedule = apps.get_model('communication', 'Schedule')
    Device = apps.get_model('communication', 'Device')
    User = apps.get_model('auth', 'User')
    
    if Schedule.objects.exists():
        print("\nSchedules table is not empty, filling aborted.")
        return

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'statics',
        'Schedule.csv'
    )

    if not os.path.exists(file_path):
        print(f"\nFile {file_path} does not exist. Aborting.")
        return

    schedules_to_create = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                # Handle NULL values for dates and numeric fields
                finish_date = None if row['finish_date'] == '' else datetime.strptime(row['finish_date'], '%Y-%m-%d').date()
                working_period = None if row['working_period'] == 'NULL' else datetime.strptime(row['working_period'], '%H:%M:%S').time()
                power_consumption = None if row['power_consumpted'] == 'NULL' else float(row['power_consumpted'])

                schedule_instance = Schedule(
                    schedule_id=int(row['schedule_id']),
                    device_id=int(row['device_id']),
                    user_id=int(row['user_id']),
                    start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                    finish_date=finish_date,
                    working_period=working_period,
                    power_consumption=power_consumption,
                    working_status=bool(int(row['working_status']))
                )
                schedules_to_create.append(schedule_instance)

        if schedules_to_create:
            Schedule.objects.bulk_create(schedules_to_create)
            print(f"\n{len(schedules_to_create)} schedules successfully loaded from {file_path}.")

    except Exception as e:
        print(f"\nError occurred while loading CSV file: {e}")
