

############### 6.1.25 #############################
    

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


########################### 9.1.25 ############################

# import cv2
# import pickle
# import os
# import numpy as np
# from YoloModels.YoloModelManager import ModelManager
# from util.image_processing import crop_image_by_points, set_text_position, get_first_frame
# from util.license_api import get_car_detail


# save_dir = 'images/parking_images'

# # ######### אם נרצה שזו תהיה תמונה ספציפית: ########
# # נשנה את הנתיב הבא לנתיב של התמונה שלנו
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

#     if not os.path.exists(original_img_path):
#         frame = get_first_frame("images/sce_parking.mp4")
#         if frame is None:
#             exit(1)

#         cv2.imwrite(original_img_path, frame)

#     initial_parking_mark()

#     model = ModelManager()

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



########################################

# from django.db import models
# from django.contrib.postgres.fields import ArrayField
# from django.core.exceptions import ValidationError
# from datetime import datetime

# # Create your models here.

# def validate_year(year):
#     current_year = datetime.now().year
#     if year > current_year or year < 1900:
#         raise ValidationError(f"Invalid Year Entered: {year}")

# class ParkingLot(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     parking_spots = models.IntegerField()
#     long = models.DecimalField(max_digits=9, decimal_places=6)
#     lat = models.DecimalField(max_digits=9, decimal_places=6)
#     isCharge = models.BooleanField(default=False)
#     payment = models.DecimalField(null=True, blank=True)
#     frame_img = models.FilePathField(null=True, unique=True)

#     def __str__ (self):
#         return f"P{"%02d" % self.id}: {self.name} with {self.parking_spots} parking spots"

# class Parking(models.Model):
#     coords = ArrayField(models.DecimalField(), size=4) 
#     parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
#     occupied = models.BooleanField(default=False)
#     disabled_parking = models.BooleanField(default=False)

#     def __str__ (self):
#         return f"P{"%02d" % self.id}"

# class User(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True, max_length=250)
#     phone_number = models.CharField(max_length=15)
#     password = models.TextField()
#     lisence_number = models.CharField(max_length=8)
#     car_type = models.CharField(max_length=50, null=True)
#     car_year = models.PositiveIntegerField(validators=[validate_year], null=True)
#     car_color = models.CharField(max_length=50, null=True)
#     car_model = models.CharField(max_length=100, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__ (self):
#         return f"P{"%02d" % self.id} {self.first_name} {self.last_name}"
    
    # def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
    #     return super().save(force_insert, force_update, using, update_fields)



############################################

# from django.contrib import admin
# from models import ParkingLot, Parking, User

# Register your models here.

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('first_name', 'last_name', 'lisence_number')
#     search_fields = ('lisence_number')


# class ParkingLotAdmin(admin.ModelAdmin):
#     pass

# class ParkingAdmin(admin.ModelAdmin):
#     list_display = ('parking_lot', 'disabled_parking', 'occupied')

# admin.register(User)
# admin.register(ParkingLot)
# admin.register(Parking)



