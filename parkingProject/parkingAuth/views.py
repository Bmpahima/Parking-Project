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
            else: 
                 return JsonResponse({'error': f'No such car: {str(lisence_plate_number)}'}, status=400)
    
            return JsonResponse({'message': 'User data processed successfully!'}, status=200)

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

            print(email_form_data, password_form_data)

            # בדיקה אם המשתמש קיים
            try:
                user = parkingAuth.objects.get(email=email_form_data)
            except parkingAuth.DoesNotExist:
                return JsonResponse({'error': 'User does not exist!'}, status=401)

            # אימות הסיסמה
            if bcrypt.checkpw(password_form_data.encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({'success': 'User logged in successfully!'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid password!'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format!'}, status=400)

        except KeyError:
            return JsonResponse({'error': 'Missing email or password in the request!'}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)