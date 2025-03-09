from django.views import View
from django.http import JsonResponse
#from django.contrib.auth import authenticate, login
#from .forms import UserRegistrationForm, UserLoginForm
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from parkingApp.util.license_api import get_car_detail
from .models import parkingAuth,ParkingHistory
#from parkingApp.models import Parking
import bcrypt
from django.contrib.sessions.models import Session 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import random 




# פונקציה להצפנת סיסמה
def hash_password(plain_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


#פונקציית הרשמה
@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View):
    def post(self, request):
        try:
            form_data = json.loads(request.body)
            print(form_data)
            lisence_plate_number = form_data['lisence_plate_number']

            car_details = get_car_detail(lisence_plate_number)
            
            if car_details :
                if parkingAuth.objects.filter(license_number=lisence_plate_number).exists():
                    return JsonResponse({'error': f'Car is already exists: {str(lisence_plate_number)}'}, status=400)
                
                year = car_details.get('year')
                car_type = car_details.get('type')
                color = car_details.get('color')
                model = car_details.get('model')
                print(year , model ,car_type ,color)

                new_user = parkingAuth.objects.create(
                    first_name = form_data['first_name'],
                    last_name = form_data['last_name'],
                    email = form_data['email'].lower(),
                    phone_number = form_data['phone_number'],
                    password = hash_password(form_data['password']),
                    license_number = form_data['lisence_plate_number'],
                    car_type = car_type,
                    car_year = year,
                    car_color = color,
                    car_model = model
                )

                new_user.is_active = True
                new_user.save()

                return JsonResponse({
                    'success': 'User logged in successfully!',
                    'user': {
                        'id': new_user.id,
                        'fname': new_user.first_name,
                        'lname': new_user.last_name,
                        'email': new_user.email,
                        'phoneNumber': new_user.phone_number,
                        'lisenceNumber': new_user.license_number
                    },
                    'isAdmin': new_user.is_admin 
                }, status=200)
            else: 
                 return JsonResponse({'error': f'No such car: {str(lisence_plate_number)}'}, status=400)
            
            

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format!'}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


#פונקציית התחברות
@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request):
        try:
            form_data = json.loads(request.body)
            email_form_data = form_data['email'].lower()
            password_form_data = form_data['password']
            # בדיקה אם המשתמש קיים
            try:
                user = parkingAuth.objects.get(email=email_form_data)
            except parkingAuth.DoesNotExist:
                return JsonResponse({'error': 'User does not exist!'}, status=401)

            # אימות הסיסמה
            if bcrypt.checkpw(password_form_data.encode('utf-8'), user.password.encode('utf-8')):
                user.is_active = True
                user.save()
                request.session['user_id'] = user.id
                return JsonResponse({
                    'success': 'User logged in successfully!',
                    'user': {
                        'id': user.id,
                        'fname': user.first_name,
                        'lname': user.last_name,
                        'email': user.email,
                        'phoneNumber': user.phone_number,
                        'lisenceNumber': user.license_number,
                    },
                    'isAdmin': user.is_admin 
                }, status=200)

            else:
                return JsonResponse({'error': 'Invalid password!'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format!'}, status=400)

        except KeyError:
            return JsonResponse({'error': 'Missing email or password in the request!'}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(View):
    def post(self, request):
        try:
            user_id = request.session.get('user_id')
            body = json.loads(request.body)
            user_id = body.get('id') 

            if not user_id:
                return JsonResponse({"error": "User ID is required."}, status=400)

            leaving_user = parkingAuth.objects.filter(id=user_id).first()

            if not leaving_user:
                return JsonResponse({"error": "User not found."}, status=404)
            request.session.flush()
            leaving_user.is_active = False
            leaving_user.save()

            return JsonResponse({'success': 'User logged out successfully!'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
        

  


def is_admin(user):
    return user.is_admin

class GetHistory(View):
    def get(self,request,userId):
        try:
            driver = parkingAuth.objects.filter(id=userId).first()
            list_history = []
            driver_history = driver.history.all()
            for history in driver_history:
                start_time_string = history.start_time.strftime("%H:%M")
                end_time_string = history.end_time.strftime("%H:%M")
                start_date_string = history.start_time.strftime("%Y-%m-%d")
                end_date_string = history.end_time.strftime("%Y-%m-%d")
                list_history.append({
                    "parking_lot":history.parking_lot.name,
                    "start_time":start_time_string,
                    "end_time":end_time_string,
                    "start_date":start_date_string,
                    "end_date":end_date_string,
                     "license_number":history.driver.license_number,
                    "first_name": history.driver.first_name,
                    "last_name": history.driver.last_name,
                })
            return JsonResponse(list_history, status=200,safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
        
class AllParksHistory(View):
    def get(self,request,parkingLotId):
        try:
            park_history = ParkingHistory.objects.filter(parking_lot__id=parkingLotId).all()
            list_history = []
            for history in park_history:
                start_time_string = history.start_time.strftime("%H:%M")
                end_time_string = history.end_time.strftime("%H:%M")
                start_date_string = history.start_time.strftime("%Y-%m-%d")
                end_date_string = history.end_time.strftime("%Y-%m-%d")
                list_history.append({
                    "parking_lot":history.parking_lot.name,
                    "start_time":start_time_string,
                    "end_time":end_time_string,
                    "start_date":start_date_string,
                    "end_date":end_date_string,
                    "license_number":history.driver.license_number,
                    "first_name": history.driver.first_name,
                    "last_name": history.driver.last_name,
                })
            return JsonResponse(list_history, status=200,safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')       
class ForgertPassword(View):
    def post(self,request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            
            if not email:
                return JsonResponse({"error": "Email is required."}, status=400)
            
            user = parkingAuth.objects.get(email=email)
            code = random.randrange(100000,999999)
            send_mail(
                "Reset Your Password",
                f"your code for reset your password is : {code}",
                settings.DEFAULT_FROM_EMAIL,##פה אנחנו צריכים להגדיר מייל שלנו דפולטיבי שממנו יישלח בעצם המייל לכולם, זה בפרונט בן.
                [user.email], 
            ) 
            return JsonResponse({"message": "Check your email for a reset link.","code": code})
        except Exception as e:
            return JsonResponse({"error": "User with this email does not exist."}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')       
class ResetPassword(View):
    def post(self,request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            new_password = data.get("new_password")
            try:
                user = parkingAuth.objects.get(email=email)
            except Exception as e:
                return JsonResponse({"error": "Invalid user"}, status=400)
            # עדכון הסיסמה החדשה (עם הצפנה)
            user.password = hash_password(new_password)
            user.save()
            return JsonResponse({"message": "Password reset successful, you can enter now with your new password."})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format!"}, status=400)
            

        
            





# class UserAdmin(View):
#     def get(self, request, id):
#         admin_users = parkingAuth.objects.filter(id=id)
#         admin_parking_data = []


            
#         for parking_lot in set([parking.parking_lot for parking in parkings]):
#             total_spots = parking_lot.parking_spots
#             occupied_spots = parkings.filter(parking_lot=parking_lot, occupied=True).count()
#             available_spots = total_spots - occupied_spots

#             parking_lots_data.append({
#                 "parking_lot_name": parking_lot.name,
#                 "total_spots": total_spots,
#                 "occupied_spots": occupied_spots,
#                 "available_spots": available_spots
#             })
        
#         admin_parking_data.append({
#             "license_number": admin.license_number,
#             "parking_lots": parking_lots_data
#         })
    
#     return JsonResponse({"admin_parking_data": admin_parking_data}, safe=False)

