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
from django.utils import timezone


def hash_password(plain_password):
    """
    Hashes a password using bcrypt.

    Args:
        plain_password (str): The user's plain password.

    Returns:
        str: A bcrypt-hashed version of the password.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


#פונקציית הרשמה
@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View):
    def post(self, request):
        """
    Handles user registration based on vehicle license plate information.

    Returns:
        JsonResponse:
            200 - User created with vehicle details.
            400 - Car exists / invalid input.
            500 - Unexpected error.
    """
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
                    car_type = car_type[::-1],
                    car_year = year,
                    car_color = color[::-1],
                    car_model = model
                )

                new_user.is_active = True
                new_user.save()

                return JsonResponse({
                    'success': 'User logged in successfully!',
                    'user': {
                        'id': new_user.id,
                        'fname': new_user.first_name.capitalize(),
                        'lname': new_user.last_name.capitalize(),
                        'email': new_user.email,
                        'phoneNumber': new_user.phone_number,
                        'lisenceNumber': new_user.license_number,
                        'car_year': new_user.car_year,
                        'car_model': new_user.car_model,
                        'car_color': new_user.car_color,
                        'car_type': new_user.car_type
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


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def post(self, request):
        """
            Authenticates a user with email and password.
        """
        try:
            form_data = json.loads(request.body)
            email_form_data = form_data['email'].lower()
            password_form_data = form_data['password']
            # Check if the user exists
            try:
                user = parkingAuth.objects.get(email=email_form_data)
            except parkingAuth.DoesNotExist:
                return JsonResponse({'error': 'User does not exist!'}, status=401)

            #password verification
            if bcrypt.checkpw(password_form_data.encode('utf-8'), user.password.encode('utf-8')):
                user.is_active = True
                user.save()
                request.session['user_id'] = user.id
                return JsonResponse({
                    'success': 'User logged in successfully!',
                    'user': {
                        'id': user.id,
                        'fname': user.first_name.capitalize(),
                        'lname': user.last_name.capitalize(),
                        'email': user.email,
                        'phoneNumber': user.phone_number,
                        'lisenceNumber': user.license_number,
                        'car_year': user.car_year,
                        'car_model': user.car_model,
                        'car_color': user.car_color,
                        'car_type': user.car_type
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
        """
            Logs out the user and invalidates session.
        """
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
    """
    Checks if a user has admin privileges.

    Args:
        user (parkingAuth): The user instance.

    Returns:
        bool: True if admin, False otherwise.
    """
    return user.is_admin

class GetHistory(View):
    def get(self,request,userId):
        """
        Returns a list of completed parking sessions for a specific user.

        URL Param:
        userId (int): The user's ID.

        Returns:
        JsonResponse: List of parking records with time and location details.
    """
        try:
            driver = parkingAuth.objects.filter(id=userId).first()
            list_history = []
            driver_history = driver.history.all()
            for history in driver_history:
                if history.end_time:
                    start_time_string = timezone.localtime(history.start_time).strftime("%H:%M")
                    end_time_string = timezone.localtime(history.end_time).strftime("%H:%M")
                    start_date_string = history.start_time.strftime("%Y-%m-%d")
                    end_date_string = history.end_time.strftime("%Y-%m-%d")
                    list_history.append({
                        "parking_lot":history.parking.parking_lot.name,
                        "parking": history.parking.id,
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
    """
    Returns a list of completed parking sessions for a specific user.

    URL Param:
        userId (int): The user's ID.

    Returns:
        JsonResponse: List of parking records with time and location details.
    """
    def get(self,request,parkingLotId):
        try:
            park_history = ParkingHistory.objects.filter(parking__parking_lot__id=parkingLotId).all()
            list_history = []
            for history in park_history:
                if history.end_time:
                    start_time_string = timezone.localtime(history.start_time).strftime("%H:%M")
                    end_time_string = timezone.localtime(history.end_time).strftime("%H:%M")
                    start_date_string = history.start_time.strftime("%Y-%m-%d")
                    end_date_string = history.end_time.strftime("%Y-%m-%d")
                    list_history.append({
                        "parking_lot":history.parking.parking_lot.name,
                        "parking": history.parking.id,
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
        """
            Sends a 6-digit reset code to the user's email for password reset.
        """
        try:
            data = json.loads(request.body)
            email = data.get("email")
            if not email:
                return JsonResponse({"error": "Email is required."}, status=400)
            
            user = parkingAuth.objects.get(email=email)
            code = str(random.randrange(100000,999999))
            send_mail(
                "Reset Your Password",
                f"your code for reset your password is : {code}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email], 
            ) 
            return JsonResponse({"message": "Check your email for a reset link.","code": code})
        except Exception as e:
            return JsonResponse({"error": "User with this email does not exist."}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')       
class ResetPassword(View):
    """
        Resets the user's password.
    """
    def post(self,request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            print(email)
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


@method_decorator(csrf_exempt, name='dispatch')
class DeleteAccount(View):
    """
        Deletes a user's account and all related data.

        URL Param:
        userId (int): ID of the user to delete.
    """
    def delete(self, request, userId):
        try:
            driver = parkingAuth.objects.get(id=userId)
            driver.delete()
            return JsonResponse({'success': "User's account deleted successfully!"}, status=200)
        
        except parkingAuth.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
