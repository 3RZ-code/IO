#!/bin/bash

echo "Waiting for PostgreSQL..."
while ! pg_isready -h db_v17 -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB; do
    sleep 1
done
echo "PostgreSQL started"

echo "Running migrations..."

python manage.py makemigrations
python manage.py migrate

echo "Creating superuser..."
python manage.py shell << EOF
from security.models import User
import os

username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='admin',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    print(f"Superuser '{username}' created successfully with role 'admin'")
else:
    # Aktualizuj istniejącego użytkownika
    user = User.objects.get(username=username)
    user.set_password(password)
    user.role = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.email = email
    user.save()
    print(f"Superuser '{username}' updated with role 'admin' and password")
EOF
echo "Superuser setup completed"

echo "Creating regular user..."
python manage.py shell << EOF
from security.models import User
import os

username = 'user'
email = 'user@example.com'
password = 'user123'

if not User.objects.filter(username=username).exists():
    User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='user',
        is_staff=False,
        is_superuser=False,
        is_active=True
    )
    print(f"User '{username}' created successfully with role 'user'")
else:
    # Aktualizuj istniejącego użytkownika
    user = User.objects.get(username=username)
    user.set_password(password)
    user.role = 'user'
    user.is_staff = False
    user.is_superuser = False
    user.is_active = True
    user.email = email
    user.save()
    print(f"User '{username}' updated with role 'user' and password")
EOF
echo "Regular user setup completed"

echo "Importing csv data..."
python manage.py shell -c "import data_acquisition.utils.import_csv as ic; ic.run()"
echo "Importing csv finished"

echo "Importing CSV data for Schedule..."
python manage.py shell -c "from communication.utils.fill_data import fill_schedules_cli; fill_schedules_cli()"
echo "Schedule import finished."

echo "Importing CSV data for Alerts..."
python manage.py shell -c "from alarm_alert.utils.fill_data import fill_alerts_cli; fill_alerts_cli()" || echo "Alert import failed."
echo "Alerts import finished."

echo "Starting server..."
python manage.py runserver 0.0.0.0:6543 