<<<<<<< HEAD
#קובץ נתיבים 
=======
from django.urls import path
from .views import ParkingLotProvider

urlpatterns = [
    path("<id>", ParkingLotProvider.as_view())
]
>>>>>>> origin/BEN-BRANCH
