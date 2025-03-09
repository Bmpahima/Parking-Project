#python -m parkingApp.initial

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')

django.setup()

import requests
import cv2
import pickle
import os
import numpy as np
from parkingApp.util.image_processing import set_text_position, get_first_frame
from parkingApp.models import Parking, ParkingLot


original_img_path = './parkingApp/images/tester.jpg'

try:
    with open('parking_coordinates.pkl', 'rb') as f:
        positionList = pickle.load(f)
except:
    positionList = []

current_pos = [] 


def get_next_id():
    return max([pos['id'] for pos in positionList]) + 1 if positionList else 0


# def save_img(img, points, id):
#     save_path = os.path.join(save_dir, f'parking_no{id}.png')

    # cv2.imwrite(save_path, crop_image_by_points(img, points))
    # print(f'Saved cropped image: {save_path}')


def mouseclick(events, x, y, flags, params):
    global current_pos

    if events == cv2.EVENT_LBUTTONDOWN:
        current_pos.append((x, y))
        print(f'Point added: {x, y}')

        if len(current_pos) == 4:
            positionList.append({
                "id": get_next_id(),
                "points": current_pos,
            })
            current_pos = []

    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(positionList):
            if cv2.pointPolygonTest(np.array(pos['points'], dtype=np.int32), (x, y), False) >= 0:
                print(f'Removed: {pos}')
                positionList.pop(i)
                break

    with open('parking_coordinates.pkl', 'wb') as f:
        pickle.dump(positionList, f)


def initial_parking_mark():
    while True:
        image = cv2.imread(original_img_path)

        for pos in positionList:
            pts = np.array(pos['points'], np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(img=image, 
                        text=f"ID: {pos['id']}", 
                        org=set_text_position(pos['points'][0], pos['points'][2]), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=0.7, 
                        color=(0, 0, 255), 
                        thickness=2)

        for pt in current_pos:
            cv2.circle(image, pt, radius=5, color=(0, 255, 0), thickness=-1)

        cv2.namedWindow("Image", cv2.WINDOW_NORMAL) 
        cv2.imshow("Image", image)
        cv2.setMouseCallback("Image", mouseclick)

        k = cv2.waitKey(1)
        if k == ord('q') or k == ord('Q'):
            break

    cv2.destroyAllWindows()



import requests

def getAddress(latitude, longitude):
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return {"error": "Invalid coordinates"}
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "accept-language": "he"  # תוצאה בעברית
        }

        headers = {"User-Agent": "MyParkingApp/1.0 (contact@example.com)"}  
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "city" in data['address']:
                return {
                    "city": data['address']['city'],
                    "road": data['address']['road'],
                }
            elif "town" in data['address']:
                return {
                    "city": data['address']['town'],
                    "road": data['address']['road'],
                }
            else:
                return {"error": "Address not found"}
        else:
            return {"error": "Address not found"}
    except:
        return {"error": "Address not found"}



def save_to_db(name, payment, long, lat):
    response = getAddress(latitude=lat,longitude=long)
    address = ""
    if 'error' in response:
        address = response['error']
    else:
        address = response['city']+ ", " +response['road']

    parking_lot = ParkingLot(
        parking_spots=len(positionList),
        name=name,
        payment=payment,
        frame_image=original_img_path,
        long=long,
        lat=lat,
        address=address,
    )

    parking_lot.save()

    parkings = []
    for p in positionList:
        new_parking = Parking(occupied=False, coords=p['points'], parking_lot=parking_lot)
        parkings.append(new_parking)

    Parking.objects.bulk_create(parkings) # sending to db in one time


if __name__ == "__main__":

    if not os.path.exists(original_img_path):
        frame = get_first_frame("./parkingApp/images/IMG_6572.mov")
        if frame is None:
            exit(1)

        cv2.imwrite(original_img_path, frame)

    initial_parking_mark()

    entered_q = input("Did you finish to mark your parking spots? (y/n)").strip()

    if entered_q =='y' or entered_q =='Y':
        try:
            name = input("What's the parking lot name? ").strip()
            pay = input("Does the parking lot have some payments? (y/n) ").strip()

            if pay =='y' or pay =='Y':
                pay = True
            elif pay == 'n' or pay == 'N':
                pay = False

            long = float(input("What's the long of the parking lot? ").strip())
            lat = float(input("What's the lat of the parking lot? ").strip())

            save_to_db(name, pay, long, lat)

            if os.path.exists('parking_coordinates.pkl'):
                os.remove('parking_coordinates.pkl')

        except Exception as e:
            print("Error occoured: ", e)

    elif entered_q =='n' or entered_q =='N':
        pass






    

    # model = ModelManager()

    # parking_image = cv2.imread(original_img_path)

    # for i in range(len(positionList)):
    #     image = crop_image_by_points(parking_image, positionList[i]["points"]) # the image of the parking
    #     vehicle_predictions = model.free_or_occupied_prediction(image)
    #     print(f" ========== car number {i} car prediction: ==========\n")
    #     print(vehicle_predictions)

    #     if vehicle_predictions and vehicle_predictions[0][0] in [0, 1]:
    #         plate_prediction = model.license_plate_prediction(image)
    #         print(f" ========== car number {i} license prediction: ==========\n")
    #         print(plate_prediction)

    #         if plate_prediction:
    #             license_plate_img = crop_image_by_points(image, plate_prediction[1])
    #             number_prediction = model.license_number_prediction(license_plate_img)
    #             print(f"========== car number {i} number prediction: ==========\n")
    #             print(number_prediction)

    #             if number_prediction:
    #                 vehicle_type = get_car_detail(number_prediction[1])
    #                 print(vehicle_type)

    