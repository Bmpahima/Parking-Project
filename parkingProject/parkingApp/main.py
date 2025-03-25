import os
import django
from datetime import datetime, timedelta
import Levenshtein
from django.http import JsonResponse
# from .firebase import send_push_notification
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')
from django.core.mail import send_mail
from django.conf import settings
django.setup()

import cv2
import pickle
import numpy as np
import requests
from parkingApp.YoloModels.YoloModelManager import ModelManager
from parkingApp.util.image_processing import crop_image_by_points, set_text_position
from parkingApp.util.email_formatting import email_format
from parkingApp.models import Parking, ParkingLot
from parkingAuth.models import ParkingHistory
from django.utils import timezone


# initialization: 
model = ModelManager() # המודלים שיצרנו: מכוניות, לוחיות ומספרים

vehicle = [0, 1] # קלאסים של כלי רכב, 0 - מכוניתת 1 - אופנוע

cap = cv2.VideoCapture('./parkingApp/images/IMG_6572.mov')
parking_lot_name = 'tester' # שם החניון הנסרק

# הגדרות לצורך סריקת החניון כל חמש פריימים
fps = cap.get(cv2.CAP_PROP_FPS)
frame = int(fps * 5)
frame_count = 0

# [Parking, Parking, Parking, Parking, Parking, Parking]
queryset = ParkingLot.objects.filter(name=parking_lot_name) # מחזיר לנו את החניון ואת כל החניות בו
if queryset.exists():
    parkingList = queryset.first().parkings.all() # מחזיר לנו את רשימת החניות בחניון
else:
    print(f"No parking lot found with name: {parking_lot_name}")
    parkingList = []


# with open('parking_coordinates.pkl', 'rb') as f:
#     positionList = pickle.load(f)

detect_validation_map = {} # מוודא שהחנייה אכן פנויה 
check_occupancy_map = {} # בודק אם החנייה תפוסה ורשומה על מישהו

# פונקציה לבדיקה אם יש רכב בכל החניות בחניון
# אם יש רכב בחניה מסוימת אנחנו מעדכנים את מצב החנייה: מעדכן רק תפוסה או פנויה         
def parking_prediction(img):
    updated_parkings = []

    for i in range(len(parkingList)):
        parking = parkingList[i]
        image = crop_image_by_points(img, parking.coords) # תמונת החנייה 

        vehicle_predictions = model.free_or_occupied_prediction(image)
        detected_classes = vehicle_predictions[0] if vehicle_predictions else [] 
        detected = any(cls in vehicle for cls in detected_classes)
        park_id = parking.id

        if detected != parking.occupied: # נבדוק אם היה שינוי במצב החנייה
            if not detected and parking.occupied: # כלומר אם קודם היה רכב ועכשיו אין רכב

                if park_id not in detect_validation_map:
                    detect_validation_map[park_id] = 1
                else:
                    detect_validation_map[park_id] += 1
            
                if detect_validation_map[park_id] >= 3:
                    parking.occupied = False

                    if parking.driver:
                        sendEmailToUser(parking.driver, "forgot")
                        # לשלוח לו מייל אל תשכח לצאתתתת

                    updated_parkings.append(parking)
                    detect_validation_map[park_id] = 0

            else: # כלומר אם קודם לא היה רכב ועכשיו יש רכב 
                if not parking.driver:
                    parking.unauthorized_parking = False
                parking.occupied = True
                detect_validation_map[parking.id] = 0
                updated_parkings.append(parking)

        elif detected == parking.occupied:
            if parking.occupied and parking.unauthorized_parking:
                if park_id not in check_occupancy_map:
                    check_occupancy_map[park_id] = 1
                else:
                    check_occupancy_map[park_id] += 1
                    print(f"check no. {check_occupancy_map[park_id]}")

            
                if check_occupancy_map[park_id] >= 20:
                    print(f"check no. {check_occupancy_map[park_id]}")
                    if parking.driver:
                        last_parked = parking.driver
                        owner = parking.parking_lot.owner.all()

                        if owner:
                            sendEmailToUser(owner[0], "admin_unknown", license_number=last_parked.license_number, phone_number=last_parked.phone_number, pid=park_id)
                        parking.driver = None
                        parking.unauthorized_parking = False
                        parking.save()
                        check_occupancy_map[park_id] = 0
                    
                    else:
                        owner = parking.parking_lot.owner.all()
                        if owner:
                            sendEmailToUser(owner[0], "unknown_car", pid=park_id)
                            parking.unauthorized_parking = False
                            parking.save()


            detect_validation_map[parking.id] = 0

    if updated_parkings: # אם יש חניות לעדכון נעדכן רקקקקקק אותןןןן!          
        Parking.objects.bulk_update(updated_parkings, ['occupied', 'unauthorized_parking'])


# פונקציה שמבצעת את הסריקה של כל החניות, ומחזירה את מספר החניות התפוסות ומספר החניות הפנויות
def liveParkingDetection(img):
    free_parking_counter = 0

    parking_prediction(img) # עדכון מצב החנייה בחניון

    for i, pos in enumerate(parkingList):
        if not pos.occupied:
            free_parking_counter += 1 # אם מצאנו חנייה פנויה

    total_spaces = len(parkingList)
    occupied_parking_spaces = total_spaces - free_parking_counter

    return img, free_parking_counter, occupied_parking_spaces # מחזירים את התמונה של החניון, מספר החניות הפנויות ומספר החניות התפוסות.


# הפונקציה שסורקת את החניון ומציגה את המסך שמראה לנו את מצב החנייה עם הסימונים על המגרש
def generate_frames():
    global frame_count, save_count

    while True:
        success, img = cap.read() 
        if not success:
            break
        
        if frame_count % frame == 0: # כל פריים חמישי נעשה סריקה של כל החניות   
            parkingList = ParkingLot.objects.filter(name=parking_lot_name)[0].parkings.all() # השגת כל החניות מהדאטה בייס
            img, free_spaces, occupied_spaces = liveParkingDetection(img) # סריקה
            saved_parking = Parking.objects.filter(is_saved=True).all() # כל החניות השמורות על ידי משתמשים
            for sp in saved_parking:
                check_parking_status(sp, crop_image_by_points(img, sp.coords)) #########check parking ---->sp
            frame_count = 0

        for parking in parkingList: # לולאה שמציירת על החלון את מספר החניות השמורות, התפוסות והפנויות
            pts = np.array(parking.coords, np.int32).reshape((-1, 1, 2))
            color = (0, 0, 255) if parking.occupied else ((255, 0, 0) if parking.is_saved else (0, 255, 0))
            cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)
            cv2.putText(img=img, 
                        text=f"ID: {parking.id}", 
                        org=set_text_position(parking.coords[0], parking.coords[2]), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=0.7, 
                        color=(0, 0, 255), 
                        thickness=2)
            
        cv2.putText(img, f"Free: {free_spaces}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) # חנייה פנויה בצבע ירוק
        cv2.putText(img, f"Saved: {len(saved_parking)}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2) # חנייה שמורה בצבע כחול
        cv2.putText(img, f"Occupied: {occupied_spaces}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) # חנייה תפוסה בצבע אדום

        cv2.imshow('Parking Detection', img)

            
        if cv2.waitKey(1) & 0xFF == ord('q'): # לסיום התוכנית נלחץ על q
            break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

# הפונקציה שבודקת את סטטוס החניות השמורות, האם הרכב ששמר את החנייה הגיע או לא
def check_parking_status(parking, park_img):
    # אם החנייה שמורה ולא תפוסה - צריך לבדוק שהנהג לא מאחר
    if not parking.occupied: 
        if parking.is_saved and parking.reserved_until < timezone.now(): # אם זמן השמירה של הבן אדם הגיע - הוא מאחר לכן נבטל את השמירה ונעדכן אותו במייל 
            sendEmailToUser(parking.driver, "late")
            parking.is_saved = False # החנייה חוזרת להיות לא שמורה ופנויה לנהגים
            parking.driver = None
            parking.save()
            

    # אם החנייה שמורה ותפוסה - זה אומר שהרכב הגיע בזמן שלו, צריך לוודא שהוא באמת הוא        
    else:
        parking.is_saved = False # קודם כל החנייה כבר לא שמורה
        parking.save()
        print(f"{parking.id} is occupied")

        actual_plate = parking.driver.license_number # מהו מספר הזהות של האדם ששמר את החנייה
        predicted_plate = model.license_plate_prediction(park_img) # מה המודל זיהה, מי האדם שפיזית חונה בחנייה כרדע
        print(f"{predicted_plate} is found")
        if predicted_plate is not None:
            
            predicted_number = model.license_number_prediction(crop_image_by_points(park_img, predicted_plate[1])) # זיהוי מספר הלוחי עצמה
            if predicted_number is not None:
                predicted_plate_number = predicted_number[1] # המספר רישוי שהמודל זיהה
                print(predicted_plate_number)

                # הפעלת מרחק לבינשטיין, עד כמה מספר הרישוי של מי שחונה בחנייה דומה למספר הזהות של האדם שאמור לחנות שם.
                similarity = 1 - Levenshtein.distance(actual_plate, predicted_plate_number) / max(len(actual_plate), len(predicted_plate_number))

                # אם המספר יחסית דומה
                if similarity >= 0.7: 
                    # parking.is_saved = False
                    # parking.save()
                    
                    sendEmailToUser(parking.driver, "arrived")
                
                # אחרת נשלח מייל לנהג ונבדוק אם זה באמת הוא
                else: 
                    sendEmailToUser(parking.driver, "taken")
            else:
                sendEmailToUser(parking.driver, "undefined")
        
        else: 
            sendEmailToUser(parking.driver, "undefined")
            # בשלב זה צריך לשלוח מייל למשתמש כדי שיאשר לנו אם זה הוא שנכנס לחנייה או לא
        



# פונקציה ששולחת מייל למשתמש
def sendEmailToUser(user, status, **kwargs):
    try:
        if status == "admin_unknown":
            email_content = email_format(status, user_name=user.first_name, userid=user.id, phone_number=kwargs['phone_number'], license_number=kwargs['license_number'], pid=kwargs['pid']) 
        elif status == "unknown_car":
            email_content = email_format(status, user_name=user.first_name, pid=kwargs['pid']) 
        else: email_content = email_format(status, user_name=user.first_name, userid=user.id) 

        # שליחה בפועל
        send_mail(
            subject=email_content['subject'],
            message=email_content['message'],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=email_content['html_message']
        )

    except Exception as e:
        print("Error sending email:", str(e))


def check_vechile_plate(license_plate):
    try:
        registered_users = parkingAuth.objects.filter(license_number__isnull=False)
        for user in registered_users: 
            similarity = 1 - Levenshtein.distance(user.license_number, license_plate) / max(len(user.license_number), len(license_plate))
            
            if similarity >= 0.9:
                return user
        return None
    except Exception as e:
        print(f"Error checking vehicle registration: {e}")
        return None 

# פונקציה ששולחת בקשה לשרת, צריך לבדוק אם זה רלוונטי
# def send_verification_to_server(request_data):
#     headers = {
#         'Content-Type': 'application/json'
#     }
    
#     response = requests.post('http://localhost:8000/parkinglot/verificationError', json=request_data,
#     headers=headers)
#     if response.status_code == 200:
#         print("Request sent successfully!")
#     else:
#         print(f"Error: {response.status_code}")


# def send_notification_to_user(request,token):
#     user_token = "USER_DEVICE_TOKEN"  # ה-Token של המשתמש מהאפליקציה
#     send_push_notification(user_token, "Time Over! the parking lot became free now.")
#     return JsonResponse({"status": "Notification sent!"})



if __name__ == "__main__":
    generate_frames()
