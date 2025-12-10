import csv
import os
from datetime import datetime
from django.db import migrations


import csv
import os
from datetime import datetime
from django.db import migrations, connection
from django.core.management.color import no_style

def reset_sequence(model_class):
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), [model_class])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)
    print(f"Sequence reset for {model_class.__name__}")

def fill_schedules(apps, schema_editor):

    Schedule = apps.get_model('communication', 'Schedule')
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

                schedule_instance = Schedule(
                    schedule_id=int(row['schedule_id']),
                    device_id=int(row['device_id']),
                    user_id=int(row['user_id']),
                    start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                    finish_date=finish_date,
                    working_period=working_period,
                    working_status=bool(int(row['working_status']))
                )
                schedules_to_create.append(schedule_instance)

        if schedules_to_create:
            Schedule.objects.bulk_create(schedules_to_create)
            print(f"\n{len(schedules_to_create)} schedules successfully loaded from {file_path}.")

    except Exception as e:
        print(f"\nError occurred while loading CSV file: {e}")


def fill_schedules_cli():
    from communication.models import Schedule
    
    # Always try to reset sequence to ensure consistency
    try:
        reset_sequence(Schedule)
    except Exception as e:
        print(f"Warning: Could not reset sequence: {e}")

    if Schedule.objects.exists():
        print("Schedules table is not empty, skipping.")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'statics', 'Schedule.csv')

    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    schedules_to_create = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    # Handle NULL values for dates and numeric fields
                    finish_date = None if row.get('finish_date', '') == '' else datetime.strptime(row['finish_date'], '%Y-%m-%d').date()
                    working_period = None if row.get('working_period', 'NULL') == 'NULL' else datetime.strptime(row['working_period'], '%H:%M:%S').time()
                    power_consumption = None if row.get('power_consumpted', 'NULL') == 'NULL' else float(row['power_consumpted'])

                    schedule_instance = Schedule(
                        schedule_id=int(row['schedule_id']) if row.get('schedule_id') else None,
                        device_id=int(row['device_id']) if row.get('device_id') else None,
                        user_id=row.get('user_id', ''),
                        start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                        finish_date=finish_date,
                        working_period=working_period,
                        working_status=bool(int(row.get('working_status', '0')))
                    )
                    schedules_to_create.append(schedule_instance)
                except Exception as e:
                    print(f"Error parsing row: {row}\n{e}")

        if schedules_to_create:
            Schedule.objects.bulk_create(schedules_to_create)
            print(f"Loaded {len(schedules_to_create)} schedules from {file_path}")
            reset_sequence(Schedule)
        else:
            print("No schedules created.")
    except Exception as e:
        print(f"Error occurred while loading CSV file: {e}")
        raise
