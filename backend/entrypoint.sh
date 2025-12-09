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
        --noinput
    echo "Superuser created successfully!"

echo "Importing csv data..."
python manage.py shell -c "import data_acquisition.utils.import_csv as ic; ic.run()"
echo "Importing csv finished"

echo "Importing CSV data for Schedule..."
python manage.py shell -c "from communication.utils.fill_data import fill_schedules_cli; fill_schedules_cli()"
echo "Schedule import finished."

echo "Starting server..."
python manage.py runserver 0.0.0.0:6543 