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
from parkingAuth.models import ParkingHistory
from django.utils import timezone
from django.core.mail import send_mail
from .models import Parking
from .main import sendEmailToUser
from .util.parkingStats import get_parking_lot_stat

class AllParkingLot (View):
    """
    Handles GET requests to retrieve all parking lots in the system.

    Returns:
        JsonResponse: A list of all parking lots, including name, location, capacity,
        number of free spots, address, and lot ID.
    """
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
                    "address": pl.address,
                    "id":pl.id
                }
                parking_lot_result.append(current_pl)

            return JsonResponse(parking_lot_result, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "No Parking Lots Available."}, status=500)


class ParkingLotProvider(View):
    """
    Handles GET requests to retrieve all parking lots in the system.

    Returns:
        JsonResponse: A list of all parking lots, including name, location, capacity,
        number of free spots, address, and lot ID.
    """
    def get(self, request, id):
        try:
            #the parking lot
            selected_parking_lot = ParkingLot.objects.get(pk=id)
            free_spots = selected_parking_lot.parking_spots - selected_parking_lot.parkings.filter(occupied=True).count()
            #the list of the parking spots of the parking lot
            parkings = selected_parking_lot.parkings.all()
            #create a dict for the info from the parking lot
            parking_lot_dict = {
                "id": selected_parking_lot.id,
                "name": selected_parking_lot.name,
                "parking_spots": selected_parking_lot.parking_spots,
                "latitude"  : selected_parking_lot.lat,
                "longitude" :  selected_parking_lot.long,
                "freeSpots": int(free_spots),
            }
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
            print(e)


@method_decorator(csrf_exempt, name='dispatch')
class SaveParking(View):
    """
    Allows a user to reserve a parking spot for a specified time.
    Creates a reservation entry and saves history.

    Request body:
        id (int): ID of the parking spot.
        user_id (int): ID of the user making the reservation.
        savetime (str): Duration type ('immediate', 'half hour', 'hour').
        we used atomic transaction - So that two people don't occupy the same parking space - only one of them will succeed

    Returns:
        JsonResponse: Success or error message.
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            id = data.get('id')
            user_id = data.get('user_id')
            savetime = data.get('savetime')
            
            with transaction.atomic():
                selected_parking = Parking.objects.select_for_update().get(id=id)
                user_parking = parkingAuth.objects.get(id=user_id)
                # if selected_parking.is_saved and selected_parking.reserved_until and selected_parking.reserved_until <= timezone.now(): # לשקול למחוק את כל התנאי הזה הוא נבדק במיין
                #     user = selected_parking.driver
                #     time_park = (selected_parking.reserved_until - timezone.now()).total_seconds() // 60
                #     # if user:
                #     #     sendEmailToUser(user, time_park)     

                #     selected_parking.is_saved = False
                #     selected_parking.driver = None
                #     selected_parking.reserved_until = None
                #     selected_parking.save()
                
                if selected_parking.occupied or selected_parking.is_saved:
                    return JsonResponse({'error':"This parking spot is not available!"}, status=400)

                if savetime == 'immediate':
                    selected_parking.is_saved = True
                    selected_parking.reserved_until = timezone.now() + timedelta(minutes=5)

                elif savetime == 'half':
                    selected_parking.is_saved = True
                    selected_parking.reserved_until = timezone.now() + timedelta(minutes=30)
                    
                elif savetime == 'hour':
                    selected_parking.is_saved = True
                    selected_parking.reserved_until = timezone.now() + timedelta(hours=1)

                selected_parking.driver = user_parking
                
                selected_parking.save()

                history = ParkingHistory(parking=selected_parking, driver=user_parking, start_time=timezone.now())
                history.save()

            return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "Error excepted"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ReleaseParking(View):
    """
    Cancels a reserved or saved parking spot by the user.
    Updates the status and history accordingly.

    Request body:
        id (int): Parking spot ID.
        user_id (int): User releasing the spot.

    Returns:
        JsonResponse: Success or relevant error message.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            parkingId = data.get('id')
            user_id = data.get('user_id')

            selected_parking = Parking.objects.get(id=parkingId) 
            user_parking = parkingAuth.objects.get(id=user_id) 
            if not selected_parking.occupied and selected_parking.is_saved:
                if selected_parking.driver != user_parking: 
                    return JsonResponse({"error": "you cannot cancel this!"},status=400)
                
                selected_parking.is_saved = False
                selected_parking.driver = None
                selected_parking.reserved_until = None
                selected_parking.unauthorized_notification_sent = False
                selected_parking.save()

                history = ParkingHistory.objects.filter(driver=user_parking, parking=selected_parking, end_time__isnull=True).first()
                if history:
                    history.end_time = timezone.now()
                    history.save()
                return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)

            elif not selected_parking.occupied and not selected_parking.is_saved:#the parking spot is not saved and not occupied
                if selected_parking.driver: #the driver get out from the spot and now want to close the app
                    selected_parking.is_saved = False
                    selected_parking.driver = None
                    selected_parking.reserved_until = None
                    selected_parking.unauthorized_notification_sent = False
                    selected_parking.save()
                    history = ParkingHistory.objects.filter(driver=user_parking, parking=selected_parking, end_time__isnull=True).first()
                    if history:
                        history.end_time = timezone.now()
                        history.save()
                    return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)
                
                else: #the parking spot is no avaliable for the driver
                    return JsonResponse({'error':"This parking spot is not available!"}, status=400) 
                
                
            else: #the spot is occupied, there is a car there
                selected_parking.unauthorized_parking = True
                selected_parking.reserved_until = None
                selected_parking.unauthorized_notification_sent = False
                selected_parking.save()

                history = ParkingHistory.objects.filter(driver=user_parking, parking=selected_parking, end_time__isnull=True).first()
                if history:
                    history.end_time = timezone.now()
                    history.save()
                return JsonResponse({"success": "Parking saved successfuly"}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "Error excepted"}, status=500)
        

class getOwnerParkingLot(View):
    """
    Returns all parking lots owned by a given admin.

    Args:
        id (int): ID of the user (owner).

    Returns:
        JsonResponse: List of parking lots with details of each spot.
    """
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
    """
    Retrieves a list of users (drivers) associated with a given parking lot.
    Includes details for users who currently occupy or have saved spots.

    Args:
        parkingLotId (int): ID of the parking lot.

    Returns:
        JsonResponse: List of parkings with associated user details.
    """
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
        
        
@method_decorator(csrf_exempt, name='dispatch')
class GetParkingStats(View):
    """
    Provides statistics for a specific parking lot for a given month and year for the parking lot manager
    Delegates computation to helper function.

    Request body:
        id (int): ID of the user (admin).
        parkinglot (int): ID of the parking lot.
        month (int): Month (1-12).
        year (int): Year (e.g., 2024).

    Returns:
        JsonResponse: Success or error if data not found.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            print(data)
            id = data.get('id')
            parking_lot_id = data.get('parkinglot')
            month = data.get('month')
            year = data.get('year')

            get_parking_lot_statistics = get_parking_lot_stat(id, parking_lot_id, month, year)
            if get_parking_lot_statistics is None:
                return JsonResponse({"error": "No data found for the given parking lot"}, status=404)
            
            return JsonResponse({"success": "success"}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}', "errorMessage": "Error excepted"}, status=500)
        


