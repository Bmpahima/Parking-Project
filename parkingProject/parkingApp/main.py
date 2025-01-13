import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')

django.setup()

import cv2
import pickle
import numpy as np
from parkingApp.YoloModels.YoloModelManager import ModelManager
from parkingApp.util.image_processing import crop_image_by_points, set_text_position
from parkingApp.models import Parking, ParkingLot


model = ModelManager()

vehicle = [0, 1]

cap = cv2.VideoCapture('./parkingApp/images/meir1.mp4')
parking_lot_name = 'raz'

fps = cap.get(cv2.CAP_PROP_FPS)
frame = int(fps * 3)
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

        if parkingList[i].occupied:
            plate_prediction = model.license_plate_prediction(image)
            print(plate_prediction)

            if plate_prediction:
                license_plate_img = crop_image_by_points(image, plate_prediction[1])
                number_prediction = model.license_number_prediction(license_plate_img)

                parkingList[i].license_number = number_prediction[1] if number_prediction else None
               
    Parking.objects.bulk_update(parkingList, ['occupied', 'license_number'])


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
            img, free_spaces, occupied_spaces = liveParkingDetection(img)
            frame_count = 0

        for parking in parkingList:
            pts = np.array(parking.coords, np.int32).reshape((-1, 1, 2))
            color = (0, 255, 0) if not parking.occupied else (0, 0, 255)

            cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)
            cv2.putText(img=img, 
                        text=f"ID: {parking.id}", 
                        org=set_text_position(parking.coords[0], parking.coords[2]), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=0.7, 
                        color=(0, 0, 255), 
                        thickness=2)
            
        cv2.putText(img, f"Free: {free_spaces}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Occupied: {occupied_spaces}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Parking Detection', img)

            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    generate_frames()
