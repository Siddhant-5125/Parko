# Generated by Django 5.1.7 on 2025-04-14 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkinguser', '0009_parkinguser_image_url_parkinguser_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkinguser',
            name='availableTypes',
            field=models.TextField(default=''),
        ),
    ]
