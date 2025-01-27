from django.views import View
from django.http import JsonResponse
from .models import ParkingLot,Parking
from datetime import datetime, timedelta
from parkingAuth.models import parkingAuth
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json


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


class ParkingLotProvider(View):
    def get(self, request, id):
        try:
            # החניון 
            selected_parking_lot = ParkingLot.objects.get(pk=id)
            free_spots = selected_parking_lot.parking_spots - selected_parking_lot.parkings.filter(occupied=True).count()
            # רשימת החניות שלו
            parkings = selected_parking_lot.parkings.all()
            #יצירת מילון למידע מהחניון
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


@method_decorator(csrf_exempt, name='dispatch')
class SaveParking(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            id = data.get('id')
            user_id = data.get('user_id')
            savetime = data.get('savetime')

            print(data)
            selected_parking_lot = Parking.objects.get(id=id)
            user_parking = parkingAuth.objects.get(id=user_id)
            

            if selected_parking_lot.occupied or selected_parking_lot.is_saved:
                return JsonResponse({'error':"This parking spot is not available!"}, status=400)
            
            if savetime == 'immediate':
                selected_parking_lot.occupied = True

            elif savetime == 'half':
                selected_parking_lot.is_saved = True
                selected_parking_lot.reserved_until = timezone.now() + timedelta(minutes=30)
                
            elif savetime == 'hour':
                selected_parking_lot.is_saved = True
                selected_parking_lot.reserved_until = timezone.now() + timedelta(hours=1)
            
            selected_parking_lot.driver = user_parking
            selected_parking_lot.save()

            return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "Error excepted"}, status=500)
            
@method_decorator(csrf_exempt, name='dispatch')
class ReleaseParking(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            id = data.get('id')
            user_id = data.get('user_id')

            print(data)
            selected_parking_lot = Parking.objects.get(id=id)
            user_parking = parkingAuth.objects.get(id=user_id)

            if not (selected_parking_lot.occupied or selected_parking_lot.is_saved):
                return JsonResponse({'error':"This parking spot is not available!"}, status=400)
        
            selected_parking_lot.occupied = False
            selected_parking_lot.driver = None
            selected_parking_lot.save()

            return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "Error excepted"}, status=500)

            


# שמירת החנייה:
# אני שומר את הזמן בדאטהבייס עבור חניות שנשמרות לא מיידית
# נניח שיש לי תוכנית בבקאנד שכל סריקה של מכוניות אני בודק אם יש חנייה שהיא משוריינת ואין בה רכב.
# אם הזמן נגמר, סלמאת.
# אם הזמן לא נגמר המשך.
# בפרונט עם ריצת הטיימר אם הגענו לזמן שבו המשתמש צריך לקום, נבדוק על ידי קריאה לדאטהסט אם החנייה תפוסה.