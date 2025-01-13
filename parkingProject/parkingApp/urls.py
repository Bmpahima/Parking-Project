from django.urls import path
from .views import ParkingLotProvider
from .views import UserRegistrationView, UserLoginView


urlpatterns = [
    path("<id>", ParkingLotProvider.as_view()),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),

]
