from django.db import models
from parkinguser.models import User,ParkingUser


class ParkingArea(models.Model):
    owner = models.ForeignKey(
        ParkingUser, on_delete=models.CASCADE, related_name='parking_area'
    )
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"Parking Area {self.id} owned by {self.owner}"



class ParkingSlots(models.Model):
    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.CASCADE
    )
    available = models.BooleanField()
    reserved = models.BooleanField()
    reserved_for_start = models.TimeField(null=True)
    reserved_for_end = models.TimeField(null=True)


class Booking(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    slot = models.ForeignKey(
        ParkingSlots,on_delete=models.CASCADE
    )
    status_choices = [('booked','booked'),('entry','entry'), ('exit','exit')]
    qr_code = models.ImageField(null=True,upload_to="qr/")
    status = models.CharField(choices=status_choices,max_length=50,default='booked')
    req_time_start = models.TimeField(null=True)
    req_time_end = models.TimeField(null=True)