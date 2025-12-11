import csv
import os
from datetime import datetime, timezone as dt_timezone
from data_acquisition.models import DeviceReading


def run():

    if DeviceReading.objects.exists():
        print(" DeviceReading table is not empty, CSV import aborted.")
        return 

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "statics", "sensors_data.csv")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            naive_dt = datetime.fromisoformat(row["timestamp"])
            aware_dt = naive_dt.replace(tzinfo=dt_timezone.utc)
            DeviceReading.objects.create(
                timestamp=aware_dt,
                device_id=row["device_id"],
                device_type=row["device_type"],
                location=row["location"],
                metric=row["metric"],
                value=float(row["value"]),
                unit=row["unit"],
                signal_dbm=int(row["signal_dbm"]),
                status=bool(row["status"]),
                name=row["name"],
                priority=int(row["priority"])
            )