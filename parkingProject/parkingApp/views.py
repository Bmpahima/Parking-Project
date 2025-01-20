from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.forms import ModelForm
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from .models import Parking, ParkingLot
from django.views import View
from django.http import JsonResponse
#from django.contrib.auth import authenticate, login
#from .forms import UserRegistrationForm, UserLoginForm
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from parkingApp.util.license_api import get_car_detail
from .models import parkingAuth
import bcrypt
# פונקציה להצפנת סיסמה
def hash_password(plain_password):
    # יצירת salt
    salt = bcrypt.gensalt()
    # הצפנת הסיסמה
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password
@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View):
    def post(self, request):
        try:
            form_data = json.loads(request.body)
            print(form_data)
            lisence_plate_number = form_data['lisence_plate_number']
            car_details = get_car_detail(lisence_plate_number)
            
            if car_details :
                year = car_details.get('year')
                car_type = car_details.get('type')
                color = car_details.get('color')
                model = car_details.get('model')
                print(year , model ,car_type ,color)
                new_user = parkingAuth.objects.create(
                    first_name = form_data['first_name'],
                    last_name = form_data['last_name'],
                    email = form_data['email'],
                    phone_number = form_data['phone_number'],
                    password = form_data['password'],
                    license_number = form_data['lisence_plate_number'],
                    car_type = car_type,
                    car_year = year,
                    car_color = color,
                    car_model = model
            )
           
    

            # החזרת תשובה במידה וכל הנתונים נקלטו בהצלחה
            return JsonResponse({'message': 'User data processed successfully!'}, status=200)

        except json.JSONDecodeError:
            # טיפול בשגיאה בפורמט JSON
            return JsonResponse({'error': 'Invalid JSON format!'}, status=400)

        except Exception as e:
            # טיפול בשגיאות לא צפויות
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

        # תשובה ברירת מחדל, במידה ולא טופל מקרה מסוים
        return JsonResponse({'error': 'Unknown error occurred'}, status=500)
# Create your views here.

class ParkingLotProvider (View):
    def get(self, request, id):
        try:
            # החניון 
            selected_parking_lot = ParkingLot.objects.get(pk=id)
            
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



# class UserRegistrationView(View):

#     def post(self, request):


#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():

#             user = form.save(commit=False) #עדיין לא שומר את הסיסמה בגלל הקומיט
#             user.set_password(form.cleaned_data['password']) #ככה אני מצפין את הסיסמה - עם סט פסוורד
#             user.save() #עכשיו הוא שומר
#             token, created = Token.objects.get_or_create(user=user) # בודק אם למשתמש יש טוקן קיים - כלומר 

#             return JsonResponse({'token': token.key}, status=200)
        
#         return JsonResponse({'errors': form.errors}, status=400)

# class UserLoginView(View):

#     def post(self, request):
#         form = UserLoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']

#             try:
#                 user = User.objects.get(username=username)
#             except User.DoesNotExist:
#                 return JsonResponse({
#                 'error': 'Invalid Username.'
#                 },
#                  status=400)

#             if check_password(password, user.password):
#                 token, created = Token.objects.get_or_create(user=user)
#                 return JsonResponse({'token': token.key}, status=200)
#             else:
#                 return JsonResponse({'error': 'Invalid email or password.'}, status=400)
#         return JsonResponse({'errors': form.errors}, status=400)

            


    
