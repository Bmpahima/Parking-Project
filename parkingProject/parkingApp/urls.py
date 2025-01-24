from django.urls import path
from .views import ParkingLotProvider,AllParkingLot
# from .views import UserRegistrationView, UserLoginView


urlpatterns = [
    path("<id>", ParkingLotProvider.as_view()),
    path("all/",AllParkingLot.as_view())
]
