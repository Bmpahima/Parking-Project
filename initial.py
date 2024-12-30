import cv2
import pickle
import os
import numpy as np
import easyocr
from ultralytics import YOLO


save_dir = 'parking_images'
original_img_path = 'parking.png'
vehicle_model = YOLO('vehicleModel.pt')
license_plate_model = YOLO('modelLicensePlate.pt')

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


def set_text_position(point1, point2):
    mid_x = ((point1[0] + point2[0]) / 2) - 24
    mid_y = ((point1[1] + point2[1]) / 2)
    return (int(mid_x), int(mid_y)) 


def cropped_img(img, points):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    points = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)

    masked_img = cv2.bitwise_and(img, img, mask=mask)

    x, y, w, h = cv2.boundingRect(points)
    cropped_img = masked_img[y:y+h, x:x+w]
    return cropped_img


def save_img(img, points, id):
    save_path = os.path.join(save_dir, f'parking_no{id}.png')

    cv2.imwrite(save_path, cropped_img(img, points))
    print(f'Saved cropped image: {save_path}')


def mouseclick(events, x, y, flags, params):
    global current_pos

    if events == cv2.EVENT_LBUTTONDOWN:
        current_pos.append((x, y))
        print(f'Point added: {x, y}')

        if len(current_pos) == 4:
            positionList.append({
                "id": get_next_id(),
                "points": current_pos,
                "occupied": False
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

def initial_prediction():
    for pos in positionList:
        cropped = cropped_img(cv2.imread(original_img_path), pos['points'])
        results = vehicle_model.predict(source=cropped, conf=0.55)
        detected_classes = results[0].boxes.cls.cpu().tolist() if results[0].boxes else []
        print(detected_classes)

       
if __name__ == "__main__":
    initial_parking_mark()
    initial_prediction()


    # for pos in positionList:
    #     print(f'Parking ID: {pos["id"]} is {"occupied" if pos["occupied"] else "free"}')
    #     print('---------------------------')

# זיהוי הרכב:

# def detect_vehicle():
#     img = cv2.imread(original_img_path)
#     for pos in positionList:
#         cropped = cropped_img(img, pos['points'])
#         results = vehicle_model.predict(source=cropped, conf=0.25)
#         detected_classes = results[0].boxes.cls.cpu().tolist() if results[0].boxes else []
#         print(detected_classes)

# detect_vehicle()
