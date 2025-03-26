from django.db import models
from django.utils.timezone import now
from parkingAuth.models import parkingAuth



class ParkingLot(models.Model):
    parking_spots = models.IntegerField()
    name = models.CharField(max_length=50)
    payment = models.BooleanField(default=False)
    frame_image = models.CharField(max_length=250)
    long = models.DecimalField(max_digits=9, decimal_places=6,null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6,null=True)
    owner = models.ManyToManyField(parkingAuth, related_name="lots", blank=True)
    address = models.TextField(max_length=200,default="Address not found")

    def __str__(self):
        return f"{self.id} Parking -{self.name}"


class Parking(models.Model):
    occupied = models.BooleanField(default=False, db_index=True) 
    coords = models.JSONField()
    parking_lot = models.ForeignKey(ParkingLot,on_delete=models.CASCADE,related_name="parkings")
    is_saved = models.BooleanField(default=False)
    reserved_until = models.DateTimeField(null=True, blank=True)
    driver = models.OneToOneField(parkingAuth, related_name='parking', null=True, on_delete=models.SET_NULL, blank=True)
    unauthorized_parking = models.BooleanField(default=False)
    unauthorized_notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pk}"



