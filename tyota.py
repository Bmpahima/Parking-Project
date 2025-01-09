# def preprocess_license_plate(img):
#     img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

#     lower_black = np.array([0, 0, 0]) 
#     upper_black = np.array([75, 75, 75])
#     lower_white = np.array([7, 170, 228])
#     upper_white = np.array([255, 255, 255])
    
#     mask = cv2.inRange(img, lower_black, upper_black)

#     highlighted_image = img.copy()
#     highlighted_image[mask > 0] = [0, 0, 0] 

#     mask1 = cv2.inRange(highlighted_image, lower_white, upper_white)
#     highlighted_image1 = highlighted_image.copy()
#     highlighted_image1[mask1 > 0] = [255, 255, 255]
    
#     # img_smoothed = cv2.GaussianBlur(license_plate, (3, 3), 1.4)

#     license_plate_gray = cv2.cvtColor(highlighted_image1, cv2.COLOR_BGR2GRAY)
    
#     # clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(5, 5))
#     # cl1 = clahe.apply(license_plate_gray)

#     # _, license_plate_thresh = cv2.threshold(cl1, 128, 255, cv2.THRESH_BINARY_INV)

#     # return license_plate_thresh
#     return license_plate_gray




# def predict_license_plate():
#     img = cropped_img(cv2.imread(original_img_path), positionList[2]['points'])

#     results = license_plate_model.predict(source=img, conf=0.25)
#     license_plate_coord = results[0].boxes.xyxy.cpu().tolist() if results[0].boxes else []
    
#     if license_plate_coord:
#         x1, y1, x2, y2 = results[0].boxes.xyxy.cpu().tolist()[0]
#         license_plate_points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

#         license_plate = cropped_img(img, license_plate_points)
#         cv2.imwrite('temp_license_plate.png', license_plate)

#         cleaned_img = preprocess_license_plate(license_plate)
#         cv2.imwrite('license_plate.png', cleaned_img)
#         read_license_plate_ocr('license_plate.png')
        




# def read_license_plate_ocr(img_path):
#     results = reader.readtext(img_path)
#     plain_text = ""
#     print(results)
#     if not results:
#         return
    
#     if len(results) > 1: 
#         for detection in results:
#             coords, text, conf = detection
#             if conf > 0.2:
#                 result_only_digits = re.sub(r'\D', '', text)
#                 plain_text += result_only_digits
#     else: 
#         plain_text = re.sub(r'\D', '', results[0][1])

#     print(plain_text)





# def preprocess_license_plate(img):
#     # img_smoothed = cv2.GaussianBlur(license_plate, (3, 3), 1.4)
#     lower_black = np.array([0, 0, 0]) 
#     upper_black = np.array([85, 85, 55])
#     mask = cv2.inRange(img, lower_black, upper_black)

#     highlighted_image = img.copy()
#     highlighted_image[mask > 0] = [0, 0, 0] 

#     license_plate_gray = cv2.cvtColor(highlighted_image, cv2.COLOR_BGR2GRAY)
    
#     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(5, 5))
#     cl1 = clahe.apply(license_plate_gray)

#     # _, license_plate_thresh = cv2.threshold(cl1, 128, 255, cv2.THRESH_BINARY_INV)

#     return license_plate_gray


############### 6.0.25 #############################
    

# import cv2
# import pickle
# import numpy as np
# from models.YoloModelManager import ModelManager
# from util.image_processing import crop_image_by_points, set_text_position


# model = ModelManager(
#         vehicle_model_path="models/VehiclesModel.pt",
#         lp_model_path="models/LicensePlateModel.pt",
#         numbers_models_path="models/LicensePlateNumModel.pt"
#     )

# vehicle = [0, 1]

# cap = cv2.VideoCapture('images/parking.mp4')

# fps = cap.get(cv2.CAP_PROP_FPS)
# frame = int(fps * 3)
# frame_count = 0
# save_count = 0

# with open('parking_coordinates.pkl', 'rb') as f:
#     positionList = pickle.load(f)

# def parking_prediction(img):
#     for pos in positionList:
#         cropped_parking_img = crop_image_by_points(img, pos['points'])
#         results = model.free_or_occupied_prediction(cropped_parking_img, conf=0.75)
#         if results:
#             detected_classes = results[0]
#             pos['occupied'] = any(cls in vehicle for cls in detected_classes)

# def liveParkingDetection(img):
#     free_parking_counter = 0

#     parking_prediction(img)

#     for i, pos in enumerate(positionList):
#         if not pos['occupied']:
#             free_parking_counter += 1

#     total_spaces = len(positionList)
#     return img, free_parking_counter, total_spaces - free_parking_counter


# def generate_frames():
#     global frame_count, save_count
#     while True:
#         success, img = cap.read()
#         if not success:
#             break
        

#         if frame_count % frame == 0:    
#             img, free_spaces, occupied_spaces = liveParkingDetection(img)
#             print(f'Free spaces: {free_spaces}, Occupied spaces: {occupied_spaces}')
#             save_count += 1

#         for pos in positionList:
#             pts = np.array(pos['points'], np.int32).reshape((-1, 1, 2))
#             color = (0, 255, 0) if not pos['occupied'] else (0, 0, 255)
#             cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)
#             cv2.putText(img=img, 
#                         text=f"ID: {pos['id']}", 
#                         org=set_text_position(pos['points'][0], pos['points'][2]), 
#                         fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
#                         fontScale=0.7, 
#                         color=(0, 0, 255), 
#                         thickness=2)

#         cv2.imshow('Parking Detection', img)

            
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#         frame_count += 1

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     generate_frames()


# import cv2
# import pickle
# import os
# import numpy as np
# from models.YoloModelManager import ModelManager
# from util.image_processing import crop_image_by_points, set_text_position
# from util.license_api import get_car_detail


# save_dir = 'images/parking_images'
# original_img_path = 'images/fourcars.jpg'


# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# try:
#     with open('parking_coordinates.pkl', 'rb') as f:
#         positionList = pickle.load(f)
# except:
#     positionList = []

# current_pos = [] 


# def get_next_id():
#     return max([pos['id'] for pos in positionList]) + 1 if positionList else 0


# def save_img(img, points, id):
#     save_path = os.path.join(save_dir, f'parking_no{id}.png')

#     cv2.imwrite(save_path, crop_image_by_points(img, points))
#     print(f'Saved cropped image: {save_path}')


# def mouseclick(events, x, y, flags, params):
#     global current_pos

#     if events == cv2.EVENT_LBUTTONDOWN:
#         current_pos.append((x, y))
#         print(f'Point added: {x, y}')

#         if len(current_pos) == 4:
#             positionList.append({
#                 "id": get_next_id(),
#                 "points": current_pos,
#                 "occupied": False,
#                 "license_number": "not found"
#             })
#             save_img(img=cv2.imread(original_img_path), 
#                      points=current_pos,
#                      id=(get_next_id() - 1))
            
#             current_pos = []

#     if events == cv2.EVENT_RBUTTONDOWN:
#         for i, pos in enumerate(positionList):
#             if cv2.pointPolygonTest(np.array(pos['points'], dtype=np.int32), (x, y), False) >= 0:
#                 print(f'Removed: {pos}')
#                 positionList.pop(i)
#                 if os.path.exists(save_dir + f'/parking_no{pos["id"]}.png'):
#                     os.remove(save_dir + f'/parking_no{pos["id"]}.png')
#                 break

#     with open('parking_coordinates.pkl', 'wb') as f:
#         pickle.dump(positionList, f)


# def initial_parking_mark():
#     while True:
#         image = cv2.imread(original_img_path)

#         for pos in positionList:
#             pts = np.array(pos['points'], np.int32).reshape((-1, 1, 2))
#             cv2.polylines(image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
#             cv2.putText(img=image, 
#                         text=f"ID: {pos['id']}", 
#                         org=set_text_position(pos['points'][0], pos['points'][2]), 
#                         fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
#                         fontScale=0.7, 
#                         color=(0, 0, 255), 
#                         thickness=2)

#         for pt in current_pos:
#             cv2.circle(image, pt, radius=5, color=(0, 255, 0), thickness=-1)

#         cv2.imshow("Image", image)
#         cv2.setMouseCallback("Image", mouseclick)

#         k = cv2.waitKey(1)
#         if k == ord('q') or k == ord('Q'):
#             break

#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     initial_parking_mark()

#     model = ModelManager(
#         vehicle_model_path="models/VehiclesModel.pt",
#         lp_model_path="models/LicensePlateModel.pt",
#         numbers_models_path="models/LicensePlateNumModel.pt"
#     )

#     parking_image = cv2.imread(original_img_path)

#     for i in range(len(positionList)):
#         image = crop_image_by_points(parking_image, positionList[i]["points"]) # the image of the parking
#         vehicle_predictions = model.free_or_occupied_prediction(image)
#         print(f" ========== car number {i} car prediction: ==========\n")
#         print(vehicle_predictions)

#         if vehicle_predictions and vehicle_predictions[0][0] in [0, 1]:
#             plate_prediction = model.license_plate_prediction(image)
#             print(f" ========== car number {i} license prediction: ==========\n")
#             print(plate_prediction)

#             if plate_prediction:
#                 license_plate_img = crop_image_by_points(image, plate_prediction[1])
#                 number_prediction = model.license_number_prediction(license_plate_img)
#                 print(f"========== car number {i} number prediction: ==========\n")
#                 print(number_prediction)

#                 if number_prediction:
#                     vehicle_type = get_car_detail(number_prediction[1])
#                     print(vehicle_type)
