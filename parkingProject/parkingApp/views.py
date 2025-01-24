from django.views import View
from django.http import JsonResponse
from django.views import View
from django.http import JsonResponse
from .models import ParkingLot
from django.views import View
from django.http import JsonResponse

class AllParkingLot (View):
    def get(self, request):
        try:
            all_parking_lots = ParkingLot.objects.all() # all parking lots

            parking_lot_result = []
            
            for pl in all_parking_lots:

                free_spots = pl.parking_spots - pl.parkings.filter(occupied=True).count()
                current_pl = {
                    "name": pl.name,
                    "latitude": pl.lat,
                    "longitude": pl.long,
                    "parking_spots": pl.parking_spots,
                    "freeSpots": int(free_spots),
                    "id":pl.id
                }
                parking_lot_result.append(current_pl)

            return JsonResponse(parking_lot_result, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "No Parking Lots Available."}, status=500)






class ParkingLotProvider (View):
    def get(self, request, id):
        try:
            # החניון 
            selected_parking_lot = ParkingLot.objects.get(pk=id)
            
            # רשימת החניות שלו
            parkings = selected_parking_lot.parkings.all()
            #יצירת מילון למידע מהחניון
            #Parking name = שם החניון
            #parking spots - כמות מקומות החנייה
            #coords - קאורדינטות
            parking_lot_dict = {
                "id": selected_parking_lot.id,
                "name": selected_parking_lot.name,
                "parking_spots": selected_parking_lot.parking_spots,
                "latitude"  : selected_parking_lot.lat,
                "longitude" :  selected_parking_lot.long,
                "freeSpots": int(free_spots),
            }
            #עיבוד רשימת מקומות החניה
            parkings_list = []


            for park in parkings: 
                current_park = {
                    "id": park.id,
                    "occupied": park.occupied,
                    "license_number": park.license_number
                }
                parkings_list.append(current_park)
            parking_lot_dict["parkings"] = parkings_list
            return JsonResponse(parking_lot_dict, status=200, safe=False)

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

            


    
