import csv
import os
from datetime import datetime, timezone as dt_timezone
from data_acquisition.models import Device, DeviceReading
from django.core.exceptions import ObjectDoesNotExist

def run():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    devices_path = os.path.join(base_dir, "statics", "devices.csv")
    readings_path = os.path.join(base_dir, "statics", "sensors_data.csv")
    
    print("Importing devices...")
    devices_imported = 0
    devices_updated = 0
    
    with open(devices_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            priority_val = int(row.get("priority", 1))
            if priority_val not in [0, 1, 2]:
                priority_val = 1
            device, created = Device.objects.get_or_create(
                device_id=int(row["device_id"]),
                defaults={
                    "name": row["name"],
                    "device_type": row["device_type"],
                    "location": row["location"],
                    "is_active": row["is_active"].lower() == "true",
                    "priority": priority_val,
                }
            )
            if not created:
                updated = False
                if device.priority != priority_val:
                    device.priority = priority_val
                    device.save()
                    updated = True
                devices_updated += 1 if updated else 0
            else:
                devices_imported += 1
    
    print(f" Devices imported: {devices_imported}, updated: {devices_updated}")

    print("Importing device readings...")
    
    old_count = DeviceReading.objects.count()
    if old_count > 0:
        print(f" Usuwanie {old_count} starych rekordów...")
        DeviceReading.objects.all().delete()
    
    imported_count = 0
    skipped_count = 0

    with open(readings_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                device = Device.objects.get(device_id=row["device_id"])

                naive_dt = datetime.fromisoformat(row["timestamp"])
                aware_dt = naive_dt.replace(tzinfo=dt_timezone.utc)
                
                reading_value = float(row["value"])
                reading_signal_dbm = int(row["signal_dbm"])
                reading_status = row["status"].lower() == "true"

                DeviceReading.objects.create(
                    device=device,
                    timestamp=aware_dt,
                    device_type=row["device_type"],
                    location=row["location"],
                    metric=row["metric"],
                    value=reading_value,
                    unit=row["unit"],
                    signal_dbm=reading_signal_dbm,
                    status=reading_status,
                )
                imported_count += 1
            
            except ObjectDoesNotExist:
                print(f" Pomięto odczyt: Brak urządzenia o ID: {row['device_id']}. Wiersz: {reader.line_num}.")
                skipped_count += 1
                
            except ValueError as e:
                print(f" Pomięto odczyt: Błąd konwersji danych w wierszu {reader.line_num}. {e}")
                skipped_count += 1
            
            except Exception as e:
                print(f" Pomięto odczyt: Nieznany błąd w wierszu {reader.line_num}. {e}")
                skipped_count += 1
                
    print(f" DeviceReadings imported. Utworzono: {imported_count}. Pominięto: {skipped_count}.")
    print("=== IMPORT COMPLETED ===")