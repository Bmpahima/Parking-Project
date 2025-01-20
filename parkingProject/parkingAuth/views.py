from django.views import View
from django.http import JsonResponse
#from django.contrib.auth import authenticate, login
#from .forms import UserRegistrationForm, UserLoginForm
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from parkingApp.util.license_api import get_car_detail
from .models import UserAuthParking
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
                new_user = UserAuthParking.objects.create(
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

        # form = UserRegistrationForm(form_data)
        # if form.is_valid():
        #     # שמירת המשתמש יחד עם הנתונים של UserProfile
        #     user = form.save()
        #     return JsonResponse({'message': 'User registered successfully!'}, status=200)
        # return JsonResponse({'errors': form.errors}, status=400)


# class UserLoginView(View):
#     def post(self, request):
#         form = UserLoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']

#             # אימות המשתמש
#             user = authenticate(username=email, password=password)
#             if user:
#                 login(request, user)

#                 # בדיקה אם למשתמש יש פרופיל מותאם אישית
#                 profile = getattr(user, 'profile', None)
#                 if profile:
#                     # שליחת מידע נוסף ללקוח מתוך UserProfile
#                     return JsonResponse({
#                         'message': 'Login successful!',
#                         'user_details': {
#                             'first_name': user.first_name,
#                             'last_name': user.last_name,
#                             'email': user.email,
#                             'phone_number': profile.phone_number,
#                             'license_plate_number': profile.license_plate_number,
#                             'car_details': {
#                                 'type': profile.car_type,
#                                 'year': profile.car_year,
#                                 'color': profile.car_color,
#                                 'model': profile.car_model,
#                             }
#                         }
#                     }, status=200)
#                 else:
#                     return JsonResponse({'message': 'Login successful, but no profile data found.'}, status=200)
#             else:
#                 return JsonResponse({'error': 'Invalid email or password!'}, status=400)
#         return JsonResponse({'errors': form.errors}, status=400)
