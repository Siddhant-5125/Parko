from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=100,null=False,help_text="User's name")
    phone = models.CharField(max_length=15, null=True, unique=True, help_text="User's phone number")
    email = models.EmailField()

    def __str__(self):
        return self.username


class ParkingUser(models.Model):
    user = models.OneToOneField(
        User, models.CASCADE, related_name='parking_owner'
    )
    parking_name = models.CharField(max_length=100,default="")
    address = models.CharField(max_length=255,default="")
    dailyRate = models.FloatField(default=0.0)
    monthlyRate = models.FloatField(default=0.0)
    openingHours = models.CharField(max_length=10,default="")
    description = models.TextField(default="")
    levels = models.IntegerField(default=1)
    total_slots = models.IntegerField()
    hourlyRate = models.FloatField()
    rating = models.FloatField(default=4.5)
    image_url = models.CharField(max_length=255,default="")
    availableTypes = models.TextField(default="")