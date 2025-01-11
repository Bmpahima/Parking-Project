from django.db import models
from django.contrib.postgres.fields import ArrayField
class ParkingLot(models.Model):

    parking_spots = models.IntegerField()
    name = models.CharField(max_length=50)
    payment = models.BooleanField(default=False)
    frame_image = models.CharField(max_length=250)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)


class Parking(models.Model):

    occupied = models.BooleanField(default=False)
    coords = ArrayField(models.DecimalField(),size=4)
    parking_lot = models.ForeignKey(ParkingLot,on_delete=models.CASCADE,related_name="parkings")

