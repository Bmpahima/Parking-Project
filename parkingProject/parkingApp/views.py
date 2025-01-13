from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from .models import Parking, ParkingLot

# Create your views here.

class ParkingLotProvider (View):
    def get(self, request, id):
        try:
            # החניון 
            selected_parking_lot = ParkingLot.objects.filter(pk=id)[0]

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

    
