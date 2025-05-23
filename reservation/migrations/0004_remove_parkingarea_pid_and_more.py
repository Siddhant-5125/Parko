# Generated by Django 5.1.7 on 2025-03-31 19:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkinguser', '0002_rename_no_slots_parkinguser_total_slots'),
        ('reservation', '0003_rename_reserved_for_parkingslots_reserved_for_end_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parkingarea',
            name='pid',
        ),
        migrations.RemoveField(
            model_name='parkingarea',
            name='req_time_end',
        ),
        migrations.RemoveField(
            model_name='parkingarea',
            name='req_time_start',
        ),
        migrations.RemoveField(
            model_name='parkingslots',
            name='slot_id',
        ),
        migrations.AlterField(
            model_name='parkingslots',
            name='parking_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.parkingarea'),
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('req_time_start', models.TimeField(null=True)),
                ('req_time_end', models.TimeField(null=True)),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.parkingslots')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parkinguser.appuser')),
            ],
        ),
    ]
