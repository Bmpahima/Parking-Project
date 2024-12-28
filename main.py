import cv2
import pickle
import numpy as np
from ultralytics import YOLO

from initial import cropped_img

model = YOLO('best.pt')
print(model.names)

vehicle = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

cap = cv2.VideoCapture('car_test.mp4')

with open('parking_coordinates.pkl', 'rb') as f:
    positionList = pickle.load(f)

def parking_prediction(img):
    for pos in positionList:
        cropped = cropped_img(img, pos['points'])
        results = model.predict(source=cropped, conf=0.25)
        detected_classes = results[0].boxes.cls.cpu().numpy() if results[0].boxes else []
        pos['occupied'] = any(cls in vehicle for cls in detected_classes)

def checkParkingSpace(img):
    free_parking_counter = 0

    parking_prediction(img)

    for i, pos in enumerate(positionList):
        color = (0, 255, 0) if not pos['occupied'] else (0, 0, 255)
        cv2.polylines(img, [np.array(pos['points'], np.int32).reshape((-1, 1, 2))], isClosed=True, color=color, thickness=2)
        if not pos['occupied']:
            free_parking_counter += 1

    total_spaces = len(positionList)
    return img, free_parking_counter, total_spaces - free_parking_counter

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

# הרץ את הפונקציה
generate_frames()
