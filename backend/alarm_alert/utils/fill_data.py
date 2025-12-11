import csv
import os
from datetime import datetime, time
from alarm_alert.models import Alert, Notification, NotificationPreferences
from security.models import User


def fill_alerts_from_csv():
    """Wypełnia bazę danych alertami z pliku CSV"""
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
                # Znajdź użytkownika jeśli podany
                user = None
                if row.get("user_email"):
                    user = User.objects.filter(email=row["user_email"]).first()

                alert_instance = Alert(
                    user=user,
                    title=row["title"],
                    description=row["description"],
                    severity=row["severity"],
                    status=row.get("status", "NEW"),
                    category=row["category"],
                    source=row["source"],
                    is_muted=row.get("is_muted", "false").lower() == "true",
                )
                alerts_to_create.append(alert_instance)
            except Exception as e:
                print(f"Error parsing row: {row}\n{e}")

    if alerts_to_create:
        Alert.objects.bulk_create(alerts_to_create)
        print(f" Loaded {len(alerts_to_create)} alerts from {file_path}")
    else:
        print("No alerts created.")


def create_sample_data():
    """Tworzy przykładowe dane dla testów"""
    
    # Pobierz użytkowników
    admin_user = User.objects.filter(role='admin').first()
    regular_user = User.objects.filter(role='user').first()
    
    if not admin_user or not regular_user:
        print("Users not found. Please create users first.")
        return
    
    # Utwórz przykładowe alerty
    alerts_data = [
        {
            'user': admin_user,
            'title': 'Critical System Alert',
            'description': 'System temperature exceeded safe limits',
            'severity': 'CRITICAL',
            'status': 'NEW',
            'category': 'system',
            'source': 'monitoring_system',
        },
        {
            'user': regular_user,
            'title': 'Energy Consumption Warning',
            'description': 'High energy consumption detected in sector B',
            'severity': 'WARNING',
            'status': 'NEW',
            'category': 'energy',
            'source': 'energy_monitor',
        },
        {
            'user': regular_user,
            'title': 'Maintenance Reminder',
            'description': 'Regular maintenance scheduled for tomorrow',
            'severity': 'INFO',
            'status': 'NEW',
            'category': 'maintenance',
            'source': 'scheduler',
        },
    ]
    
    for alert_data in alerts_data:
        Alert.objects.create(**alert_data)
    
    print(f"Created {len(alerts_data)} sample alerts")
    
    # Utwórz preferencje powiadomień
    NotificationPreferences.objects.get_or_create(
        user=admin_user,
        defaults={
            'quiet_hours_start': time(22, 0),
            'quiet_hours_end': time(7, 0),
            'is_active': True,
        }
    )
    
    NotificationPreferences.objects.get_or_create(
        user=regular_user,
        defaults={
            'quiet_hours_start': time(23, 0),
            'quiet_hours_end': time(8, 0),
            'is_active': True,
        }
    )
    
    print("Created notification preferences for users")


def fill_alerts_cli():
    """Funkcja wywoływana z CLI"""
    print("Importing CSV data for Alerts...")
    fill_alerts_from_csv()
    print("Alerts import finished.")

