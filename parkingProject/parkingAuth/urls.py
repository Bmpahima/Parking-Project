from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView,AllParksHistory,GetHistory


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('history/<int:userId>/', GetHistory.as_view(), name='userhistory'),
    path('admin/history/<int:parkingLotId>/', AllParksHistory.as_view(), name='history'),

]