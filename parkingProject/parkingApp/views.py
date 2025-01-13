from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.forms import ModelForm
from django.views import View
from django.http import JsonResponse
from .forms import UserRegistrationForm, UserLoginForm
from .models import User
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from .models import Parking, ParkingLot,User

# Create your views here.

class ParkingLotProvider (View):
    def get(self, request, id):
        try:
            # החניון 
            selected_parking_lot = ParkingLot.objects.get(pk=id)[0]
            
            # רשימת החניות שלו
            parkings = selected_parking_lot.parkings.all()

            parking_lot_dict = {
                "parkingName": selected_parking_lot.name,
                "parkingSpots": selected_parking_lot.parking_spots,
                "coords": [selected_parking_lot.lat, selected_parking_lot.long]
            }

            parkings_list = []

            for park in parkings: 
                current_park = {
                    "id": park.id,
                    "occupied": park.occupied,
                    "license_number": park.license_number
                }
                parkings_list.append(current_park)

            return JsonResponse({"parkinglot": parking_lot_dict, "parkings": parkings_list})

        except Exception as e:
            pass



class UserRegistrationView(View):
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # הצפנת סיסמה
            user.save()
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key}, status=200)
        return JsonResponse({'errors': form.errors}, status=400)

class UserLoginView(View):
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid email or password.'}, status=400)

            if check_password(password, user.password):
                token, created = Token.objects.get_or_create(user=user)
                return JsonResponse({'token': token.key}, status=200)
            else:
                return JsonResponse({'error': 'Invalid email or password.'}, status=400)
        return JsonResponse({'errors': form.errors}, status=400)

            


    
