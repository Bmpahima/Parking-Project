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

    def __str__(self):
        return f"{self.id} - {self.name}"


class Parking(models.Model):
    occupied = models.BooleanField(default=False) 
    coords = models.JSONField(models.IntegerField())
    parking_lot = models.ForeignKey(ParkingLot,on_delete=models.CASCADE,related_name="parkings")
    license_number = models.CharField(max_length=8, null=True)
    is_saved = models.BooleanField(default=False)
    reserved_until = models.DateTimeField(null=True, blank=True)
    driver = models.OneToOneField(parkingAuth,related_name='parking',null = True,on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.id}"


# class parkingAuth(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True, max_length=250)
#     phone_number = models.CharField(max_length=10, unique=True)
#     password = models.TextField()
#     license_number = models.CharField(max_length=8)
#     car_type = models.CharField(max_length=50, null=True)
#     car_year = models.PositiveIntegerField(null=True)
#     car_color = models.CharField(max_length=50, null=True)
#     car_model = models.CharField(max_length=100, null=True)
#     created_at = models.DateTimeField(default=now)  # Automatically set the timestamp on creation

#     def __str__(self):

#         return f"{self.first_name} {self.last_name}"

