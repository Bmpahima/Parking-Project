from django.db import models
from django.utils.timezone import now
# from parkingApp.models import ParkingLot

class parkingAuth(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=250)
    phone_number = models.CharField(max_length=10, unique=True)
    password = models.TextField()
    license_number = models.CharField(max_length=8)
    car_type = models.CharField(max_length=50, null=True)
    car_year = models.PositiveIntegerField(null=True)
    car_color = models.CharField(max_length=50, null=True)
    car_model = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(default=now)  # Automatically set the timestamp on creation
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User Name'
    def __str__(self):

        return f"{self.first_name} {self.last_name} - {self.license_number}"
