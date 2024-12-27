import cv2
import pickle
import numpy as np
from ultralytics import YOLO

from initial import cropped_img

model = YOLO('yolov8l.pt')

cap = cv2.VideoCapture('car_test.mp4')

with open('parking_coordinates.pkl', 'rb') as f:
    positionList = pickle.load(f)
    
def parking_prediction(img):
    for pos in positionList:
        results = model.predict(source=cropped_img(img, pos['points']), conf=0.25)
        print(results[0].boxes.cls)
        print(results[0].names[67])
        print(f'Parking ID: {pos["id"]} is {"occupied" if pos["occupied"] else "free"}')

def checkParkingSpace(img):
    free_parking_counter = 0

    parking_prediction(img)

    for i, pos in enumerate(positionList):
        if pos['occupied']:
            cv2.polylines(img, [np.array(pos['points'], np.int32).reshape((-1, 1, 2))], isClosed=True, color=(0, 0, 255), thickness=2)
        else:
            cv2.polylines(img, [np.array(pos['points'], np.int32).reshape((-1, 1, 2))], isClosed=True, color=(0, 255, 0), thickness=2)
            free_parking_counter += 1

    totalSpaces = len(positionList)

    return img, free_parking_counter, totalSpaces - free_parking_counter

def generate_frames():
    while True:
        success, img = cap.read()
        if not success:
            break

        img, free_spaces, occupied_spaces = checkParkingSpace(img)
        print(f'Free spaces: {free_spaces}, Occupied spaces: {occupied_spaces}')
        
        cv2.imshow('Parking Detection', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

generate_frames()