from django.views import View
from django.http import JsonResponse
#from django.contrib.auth import authenticate, login
#from .forms import UserRegistrationForm, UserLoginForm
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from parkingApp.util.license_api import get_car_detail
from .models import parkingAuth
from parkingApp.models import Parking
import bcrypt
from django.contrib.sessions.models import Session 

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

