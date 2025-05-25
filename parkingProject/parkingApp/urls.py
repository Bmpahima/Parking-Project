from django.urls import path
from .views import ParkingLotProvider, AllParkingLot, SaveParking, ReleaseParking, getOwnerParkingLot, getParkingLotUsers, GetParkingStats
# from .views import UserRegistrationView, UserLoginView

# URL Configuration for parkingApp endpoints
urlpatterns = [
    path("<int:id>", ParkingLotProvider.as_view()),
    path("all/",AllParkingLot.as_view()),
    path("book/", SaveParking.as_view()),
    path("unbook/", ReleaseParking.as_view()),
    path("admin_parking_lots/<int:id>/", getOwnerParkingLot.as_view()),
    path("parking_lot_users/<int:parkingLotId>/", getParkingLotUsers.as_view()),
    path("stats/", GetParkingStats.as_view()),
]
