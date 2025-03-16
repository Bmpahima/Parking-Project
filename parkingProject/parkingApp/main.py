import os
import django
from datetime import datetime, timedelta
import Levenshtein
from django.http import JsonResponse
from .firebase import send_push_notification
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')
from django.core.mail import send_mail
from django.conf import settings
django.setup()

import cv2
import pickle
import numpy as np
import requests
from parkingApp.YoloModels.YoloModelManager import ModelManager
from parkingApp.util.image_processing import crop_image_by_points, set_text_position
from parkingApp.models import Parking, ParkingLot
from django.utils import timezone



model = ModelManager()

vehicle = [0, 1]

cap = cv2.VideoCapture('./parkingApp/images/IMG_6572.mov')
parking_lot_name = 'tester'

fps = cap.get(cv2.CAP_PROP_FPS)
frame = int(fps * 5)
frame_count = 0

# [Parking, Parking, Parking, Parking, Parking, Parking]
parkingList = ParkingLot.objects.filter(name=parking_lot_name)[0].parkings.all()

# with open('parking_coordinates.pkl', 'rb') as f:
#     positionList = pickle.load(f)

def parking_prediction(img):
    for i in range(len(parkingList)):
        image = crop_image_by_points(img, parkingList[i].coords) # the image of the parking
        vehicle_predictions = model.free_or_occupied_prediction(image)

        detected_classes = vehicle_predictions[0] if vehicle_predictions else []
        parkingList[i].occupied = any(cls in vehicle for cls in detected_classes)
               
    Parking.objects.bulk_update(parkingList, ['occupied'])


def liveParkingDetection(img):
    free_parking_counter = 0

    parking_prediction(img)

    for i, pos in enumerate(parkingList):
        if not pos.occupied:
            free_parking_counter += 1

    total_spaces = len(parkingList)
    occupied_parking_spaces = total_spaces - free_parking_counter

    return img, free_parking_counter, occupied_parking_spaces


def generate_frames():
    global frame_count, save_count
    while True:

        success, img = cap.read()
        if not success:
            break
        
        if frame_count % frame == 0:    
            parkingList = ParkingLot.objects.filter(name=parking_lot_name)[0].parkings.all()
            img, free_spaces, occupied_spaces = liveParkingDetection(img)
            saved_parking = Parking.objects.filter(is_saved=True).all()
            for sp in saved_parking:
                check_parking_status(sp, crop_image_by_points(img, sp.coords))#########check parking ---->sp
            frame_count = 0

        for parking in parkingList:
            pts = np.array(parking.coords, np.int32).reshape((-1, 1, 2))
            color = (0, 0, 255) if parking.occupied else ((255, 0, 0) if parking.is_saved else (0, 255, 0))
            cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)
            cv2.putText(img=img, 
                        text=f"ID: {parking.id}", 
                        org=set_text_position(parking.coords[0], parking.coords[2]), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=0.7, 
                        color=(0, 0, 255), 
                        thickness=2)
            
        cv2.putText(img, f"Free: {free_spaces}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Saved: {len(saved_parking)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, f"Occupied: {occupied_spaces}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


        cv2.imshow('Parking Detection', img)

            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

def check_parking_status(parking, park_img):
    if not parking.occupied:
        if parking.is_saved and parking.reserved_until < timezone.now():
            parking.is_saved = False
            parking.driver = None
            parking.save()
            request_data = {
                'verified': False,
                'message': "User didn't arrived to the parking in time!"
            }
            send_verification_to_server(request_data=request_data)
            
    else:
        parking.is_saved = False
        parking.save()
        request_data = {
            'verified': False,
            'message': 'User has not been verified!'
        }

        actual_plate = parking.driver.license_number
        predicted_plate = model.license_plate_prediction(park_img)
        if predicted_plate is not None:
            predicted_number = model.license_number_prediction(crop_image_by_points(park_img, predicted_plate[1]))
            if predicted_number is not None:
                predicted_plate_number = predicted_number[1]

                similarity = 1 - Levenshtein.distance(actual_plate, predicted_plate_number) / max(len(actual_plate), len(predicted_plate_number))
                if similarity >= 0.7:
                    parking.is_saved = False
                    parking.save()
                    request_data['verified'] = True
                    request_data['message'] = 'User has been verified!'
                    sendMailCases(parking.driver, "recognize")
                else:
                    parking.unauthorized_parking = True
                    parking.save()
                    request_data['verified'] = False
                    request_data['message'] = f"Unauthorized vehicle detected in parking {parking.id}. Expected: {actual_plate}, Found: {predicted_plate_number}"
                    sendMailCases(parking.driver, "a")
        
        send_verification_to_server(request_data)


def send_verification_to_server(request_data):
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post('http://localhost:8000/parkinglot/verificationError', json=request_data,
    headers=headers)
    if response.status_code == 200:
        print("Request sent successfully!")
    else:
        print(f"Error: {response.status_code}")

def sendMailCases(user,time_park):
    if time_park =="a":
        send_mail("Unauthorized vehicle detected in your reserved parking spot!",
                "someone else has been entered to your parking!",
                settings.DEFAULT_FROM_EMAIL,[user.email])
    elif time_park == "recognize":
        send_mail("We recognize you at the parking!",
                f"Hello {user.name}, we recognize you at the parking lot! enjoy your parking!",
                settings.DEFAULT_FROM_EMAIL,[user.email])
    else:
        send_mail("Your parking is not saved anymore!",
              f"The parking that you saved for {time_park} minutes, is not saved anymore.",
              settings.DEFAULT_FROM_EMAIL,[user.email])





# def send_notification_to_user(request,token):
#     user_token = "USER_DEVICE_TOKEN"  # ה-Token של המשתמש מהאפליקציה
#     send_push_notification(user_token, "Time Over! the parking lot became free now.")
#     return JsonResponse({"status": "Notification sent!"})




if __name__ == "__main__":
    generate_frames()
