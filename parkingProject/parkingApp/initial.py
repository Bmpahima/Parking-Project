import cv2
import pickle
import os
import numpy as np
from YoloModels.YoloModelManager import ModelManager
from util.image_processing import crop_image_by_points, set_text_position, get_first_frame
from util.license_api import get_car_detail
from .models import Parking,ParkingLot


save_dir = 'images/parking_images'

# ######### אם נרצה שזו תהיה תמונה ספציפית: ########
# נשנה את הנתיב הבא לנתיב של התמונה שלנו


original_img_path = 'images/fourcars.jpg'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

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
                "occupied": False,
                "license_number": "not found"
            })
            save_img(img=cv2.imread(original_img_path), 
                     points=current_pos,
                     id=(get_next_id() - 1))
            
            current_pos = []

    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(positionList):
            if cv2.pointPolygonTest(np.array(pos['points'], dtype=np.int32), (x, y), False) >= 0:
                print(f'Removed: {pos}')
                positionList.pop(i)
                if os.path.exists(save_dir + f'/parking_no{pos["id"]}.png'):
                    os.remove(save_dir + f'/parking_no{pos["id"]}.png')
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

        cv2.imshow("Image", image)
        cv2.setMouseCallback("Image", mouseclick)

        k = cv2.waitKey(1)
        if k == ord('q') or k == ord('Q'):
            break

    cv2.destroyAllWindows()

def save_to_db(name,payment,long,lat):
    parking_lot = ParkingLot(
        parking_spots=len(positionList),
        name=name,
        payment=payment,
        frame_image=original_img_path,
        long=long,
        lat=lat
    )
    parking_lot.save()
    parkings = []
    for p in positionList:
        new_parking = Parking(occupied=False,coords=p['points'],parking_lot=parking_lot)
        parkings.append(new_parking)
    Parking.objects.bulk_create(parkings) ##sending to db in one time


if __name__ == "__main__":

    if not os.path.exists(original_img_path):
        frame = get_first_frame("images/sce_parking.mp4")
        if frame is None:
            exit(1)

        cv2.imwrite(original_img_path, frame)
    

    initial_parking_mark()
    entered_q = input("Did you finish to mark your parking spots? ")

    

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

    