import csv
import os 
from datetime import datetime
from django.db import migrations

def fill_reports(apps, schema_editor):
    
    Report = apps.get_model('analysis_reporting', 'Report')
    
    if Report.objects.exists():
        print("\nReports table is not empty, filling aborted.")
        return

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'statics',  
        'reports_data.csv'
    )

    if not os.path.exists(file_path):
        print(f"\nFile {file_path} does not exist. Aborting.")
        return

    reports_to_create = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            
            reader = csv.DictReader(csv_file)

            for row in reader:
                user_id = int(row['created_by_id']) if row['created_by_id'] else None
                created_time = datetime.strptime(row['created_timestamp'], '%Y-%m-%d %H:%M:%S')
                date_from = datetime.strptime(row['date_from'], '%Y-%m-%d').date()
                date_to = datetime.strptime(row['date_to'], '%Y-%m-%d').date()

                report_instance = Report(
                    created_by_id=user_id,
                    created_timestamp=created_time,
                    report_type=row['report_type'],
                    report_frequency=row['report_frequency'],
                    date_from=date_from,
                    date_to=date_to
                )
                
                reports_to_create.append(report_instance)

        if reports_to_create:
            Report.objects.bulk_create(reports_to_create)
            print(f"Reports successfully loaded from {file_path}.")

    except Exception as e:
        print(f"\nWystąpił błąd podczas wczytywania pliku CSV: {e}")

