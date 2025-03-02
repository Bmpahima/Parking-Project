from django.views import View
from django.http import JsonResponse
from .models import ParkingLot,Parking
from datetime import datetime, timedelta
from parkingAuth.models import parkingAuth
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
from django.db import transaction



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
                    "saved": park.is_saved
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
            with transaction.atomic():
                selected_parking = Parking.objects.select_for_update().get(id=id)
                user_parking = parkingAuth.objects.get(id=user_id)
                print("1")
                if selected_parking.occupied or selected_parking.is_saved:
                    print("2")
                    return JsonResponse({'error':"This parking spot is not available!"}, status=400)

                if savetime == 'immediate':
                    selected_parking.is_saved = True
                    selected_parking.reserved_until = timezone.now() + timedelta(minutes=5)

                elif savetime == 'half':
                    print("ben")
                    selected_parking.is_saved = True
                    selected_parking.reserved_until = timezone.now() + timedelta(minutes=30)
                    print("3")
                    
                elif savetime == 'hour':
                    selected_parking.is_saved = True
                    selected_parking.reserved_until = timezone.now() + timedelta(hours=1)

                selected_parking.driver = user_parking
                
                selected_parking.save()
                print('dd')
            return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "Error excepted"}, status=500)
            

@method_decorator(csrf_exempt, name='dispatch')
class ReleaseParking(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            parkingId = data.get('id')
            user_id = data.get('user_id')

            print(data)

            selected_parking = Parking.objects.get(id=parkingId) #חניה
            user_parking = parkingAuth.objects.get(id=user_id) #משתמש
            if not selected_parking.occupied and selected_parking.is_saved:
                if selected_parking.driver != user_parking:
                    return JsonResponse({"error": "you cannot cancel this!"},status=400)
                
                selected_parking.is_saved = False
                selected_parking.driver = None
                selected_parking.reserved_until = None
                selected_parking.save()
                return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)


            elif not (selected_parking.occupied or selected_parking.is_saved):
                return JsonResponse({'error':"This parking spot is not available!"}, status=400)
        
            else:
                selected_parking.occupied = False
                selected_parking.driver = None
                selected_parking.reserved_until = None
                selected_parking.save()
                return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "Error excepted"}, status=500)
        

class getOwnerParkingLot(View):
    def get(self, request, id):
        try:
            user = parkingAuth.objects.filter(id=id).first()
            
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            owner_parking_lots = user.lots.all()
            print(owner_parking_lots)
            parking_lots_list = []
            for parking_lot in owner_parking_lots:
                free_spots = parking_lot.parking_spots - parking_lot.parkings.filter(occupied=True).count()
                
                parkings_list = [
                    {
                        "id": park.id,
                        "occupied": park.occupied,
                        "license_number": park.driver.license_number if park.occupied and park.driver else None
                    }
                    for park in parking_lot.parkings.all()
                ]
                
                parking_lots_list.append({
                    "id": parking_lot.id,
                    "name": parking_lot.name,
                    "latitude": float(parking_lot.lat) if parking_lot.lat else None,
                    "longitude": float(parking_lot.long) if parking_lot.long else None,
                    "parking_spots": parking_lot.parking_spots,
                    "freeSpots": int(free_spots),
                    "parkings": parkings_list
                })

            return JsonResponse(parking_lots_list, status=200, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        

class getParkingLotUsers(View):
    def get(self, request, parkingLotId):
        try:
            parking_lot = ParkingLot.objects.filter(id=parkingLotId).first()
            if not parking_lot:
                return JsonResponse({"error": "Parking lot not found"}, status=404)

            parkings = parking_lot.parkings.all()

            parkings_list = [
                {
                    "id": park.id,
                    "occupied": park.occupied,
                    "saved": park.is_saved,
                    "user": {
                        "id": park.driver.id,
                        "first_name": park.driver.first_name,
                        "last_name": park.driver.last_name,
                        "email": park.driver.email,
                        "phone_number": park.driver.phone_number,
                        "license_number": park.driver.license_number,
                        "car_type": park.driver.car_type,
                        "car_model": park.driver.car_model,
                        "car_color": park.driver.car_color[::-1],
                        "car_year": park.driver.car_year,
                    } if (park.occupied or park.is_saved) and park.driver else None
                }
                for park in parkings
            ]

            return JsonResponse({"parkings": parkings_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        
        ############################################################################################################################
                                                                #TO DO

        ############################################################################################################################
            

# שמירת החנייה:
# אני שומר את הזמן בדאטהבייס עבור חניות שנשמרות לא מיידית
# נניח שיש לי תוכנית בבקאנד שכל סריקה של מכוניות אני בודק אם יש חנייה שהיא משוריינת ואין בה רכב.
# אם הזמן נגמר, סלמאת.
# אם הזמן לא נגמר המשך.
# בפרונט עם ריצת הטיימר אם הגענו לזמן שבו המשתמש צריך לקום, נבדוק על ידי קריאה לדאטהסט אם החנייה תפוסה.