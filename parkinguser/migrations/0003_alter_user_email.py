# Generated by Django 5.1.7 on 2025-04-12 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkinguser', '0002_rename_no_slots_parkinguser_total_slots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
