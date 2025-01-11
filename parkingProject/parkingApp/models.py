from django.db import models
from django.contrib.postgres.fields import ArrayField


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
    coords = ArrayField(models.DecimalField(decimal_places=8,max_digits=9),size=4)
    parking_lot = models.ForeignKey(ParkingLot,on_delete=models.CASCADE,related_name="parkings")

    def __str__(self):
        return f"{self.id}"

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=250)
    phone_number = models.CharField(max_length=10)
    password = models.TextField()
    license_number = models.CharField(max_length=8)
    car_type = models.CharField(max_length=50, null=True)
    car_year = models.PositiveIntegerField(null=True)
    car_color = models.CharField(max_length=50, null=True)
    car_model = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"