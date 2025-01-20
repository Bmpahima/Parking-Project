from django.urls import path
from .views import ParkingLotProvider
# from .views import UserRegistrationView, UserLoginView


urlpatterns = [
    path("<id>", ParkingLotProvider.as_view()),
]
