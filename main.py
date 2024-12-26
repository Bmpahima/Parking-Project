import cv2
import pickle
import numpy as np
import math
from model import make_prediction
from test import cropped_img

cap = cv2.VideoCapture('car_test.mp4')

def get_width_and_height(points):
    width = math.dist(points[0], points[1])
    height = math.dist(points[1], points[2])
    return width, height

with open('parking_coordinates.pkl', 'rb') as f:
    positionList = pickle.load(f)

def checkParkingSpace(img):
    free_parking_counter = 0
    parking_spots = []

    for pos in positionList:
        points = pos['points']
        parking_spot = cropped_img(img, points)
        parking_spots.append(parking_spot)

    predictions = make_prediction(parking_spots)

    for i, pos in enumerate(positionList):
        pass
        # draw the parking spots
        
    totalSpaces = len(positionList)


    return img, free_parking_counter, totalSpaces - free_parking_counter

def generate_frames():
    while True:
        success, img = cap.read()
        if not success:
            break

        img, free_spaces, occupied_spaces = checkParkingSpace(img)
        ret, buffer = cv2.imencode('.jpg', img)
        img = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
