# Generated by Django 5.1.7 on 2025-04-14 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parkinguser', '0004_parkinguser_parking_name_delete_appuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
    ]
