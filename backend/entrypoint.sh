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
python manage.py createsuperuser \
    --email $DJANGO_SUPERUSER_EMAIL \
    --username $DJANGO_SUPERUSER_USERNAME \
    --noinput 2>/dev/null || echo "Superuser already exists"
echo "Superuser setup completed"

echo "Importing csv data..."
python manage.py shell -c "import data_acquisition.utils.import_csv as ic; ic.run()"
echo "Importing csv finished"

echo "Importing CSV data for Alerts..."
python manage.py shell -c "from alarm_alert.utils.fill_data import fill_alerts_from_csv; fill_alerts_from_csv()" || echo "Alert import failed."
echo "Alerts import finished."

echo "Starting server..."
python manage.py runserver 0.0.0.0:6543 