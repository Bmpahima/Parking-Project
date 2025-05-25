from django.db import models
from django.utils.timezone import now

class parkingAuth(models.Model):

    """
    Represents a registered driver in the parking system.

    Attributes:
        first_name (str): Driver's first name.
        last_name (str): Driver's last name.
        email (str): Unique email address used for login or notifications.
        phone_number (str): Unique 10-digit phone number.
        password (str): Encrypted password or hash.
        license_number (str): Driver's license plate number (indexed for faster lookups).
        car_type (str): Manufacturer or type of the vehicle.
        car_year (int): Year the car was manufactured.
        car_color (str): Color of the vehicle.
        car_model (str): Commercial model name.
        created_at (datetime): Timestamp when the driver registered.
        is_active (bool): Indicates whether the account is active.
        is_admin (bool): Indicates if the user has admin privileges.

    Meta:
        verbose_name (str): Custom name shown in the Django admin panel.

    Methods:
        __str__(): Returns a human-readable identifier of the user.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=250)
    phone_number = models.CharField(max_length=10, unique=True)
    password = models.TextField()
    license_number = models.CharField(max_length=8, db_index=True)
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

class ParkingHistory(models.Model):
    """
    Represents a single parking event, tracking when a user parked and when they left.

    Attributes:
        parking (ForeignKey): Link to the specific parking spot (nullable).
        driver (ForeignKey): Reference to the user who parked.
        start_time (datetime): When the vehicle entered the parking spot.
        end_time (datetime): When the vehicle exited the parking spot.
    """
    parking = models.ForeignKey('parkingApp.Parking', on_delete=models.CASCADE, related_name="history", null=True)
    driver = models.ForeignKey('parkingAuth.parkingAuth', on_delete=models.CASCADE, related_name="history")
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True)
    