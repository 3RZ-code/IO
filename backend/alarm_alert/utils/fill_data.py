import csv
import os
from datetime import datetime
from alarm_alert.models import Alert


def fill_alerts_from_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "statics", "alerts_data.csv")

    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    if Alert.objects.exists():
        print("Alert table not empty — skipping.")
        return

    alerts_to_create = []

    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                alert_instance = Alert(
                    user_id=int(row["user_id"]) if row["user_id"] else None,
                    device_id=int(row["device_id"]) if row["device_id"] else None,
                    timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S"),
                    source=row["source"],
                    category=row["category"],
                    severity=row["severity"],
                    message=row["message"],
                    details=row["details"],
                    status=row["status"],
                    is_quiet_hours=row["is_quiet_hours"].lower() == "true",
                    notified=row["notified"].lower() == "true",
                    deleted=row["deleted"].lower() == "true",
                    visible_for=row["visible_for"],
                )
                alerts_to_create.append(alert_instance)
            except Exception as e:
                print(f"Error parsing row: {row}\n{e}")

    if alerts_to_create:
        Alert.objects.bulk_create(alerts_to_create)
        print(f" Loaded {len(alerts_to_create)} alerts from {file_path}")
    else:
        print("No alerts created.")
