import cv2
import pickle
import numpy as np
from YoloModels.YoloModelManager import ModelManager
from util.image_processing import crop_image_by_points, set_text_position

model = ModelManager()

vehicle = [0, 1]

cap = cv2.VideoCapture('images/sce_parking.mp4')

fps = cap.get(cv2.CAP_PROP_FPS)
frame = int(fps * 3)
frame_count = 0

with open('parking_coordinates.pkl', 'rb') as f:
    positionList = pickle.load(f)

def parking_prediction(img):
    for pos in positionList:
        cropped_parking_img = crop_image_by_points(img, pos['points'])
        results = model.free_or_occupied_prediction(cropped_parking_img, conf=0.80)
        if results:
            detected_classes = results[0]
            pos['occupied'] = any(cls in vehicle for cls in detected_classes)


def liveParkingDetection(img):
    free_parking_counter = 0

    parking_prediction(img)

    for i, pos in enumerate(positionList):
        if not pos['occupied']:
            free_parking_counter += 1

    total_spaces = len(positionList)
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

        for pos in positionList:
            pts = np.array(pos['points'], np.int32).reshape((-1, 1, 2))
            color = (0, 255, 0) if not pos['occupied'] else (0, 0, 255)
            cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)
            cv2.putText(img=img, 
                        text=f"ID: {pos['id']}", 
                        org=set_text_position(pos['points'][0], pos['points'][2]), 
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
