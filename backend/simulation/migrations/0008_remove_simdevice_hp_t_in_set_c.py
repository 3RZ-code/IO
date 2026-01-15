from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("simulation", "0007_batterylog"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "ALTER TABLE simulation_simdevice DROP COLUMN IF EXISTS hp_t_in_set_c;",
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[],
        ),
    ]
