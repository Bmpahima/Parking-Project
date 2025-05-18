# daphne -p 8000 parkingProject.asgi:application

import os
import django
import Levenshtein

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')
# django.setup()

from django.core.mail import send_mail
from django.conf import settings
import cv2
import numpy as np
from parkingApp.YoloModels.YoloModelManager import ModelManager
from parkingApp.util.image_processing import crop_image_by_points, set_text_position
from parkingApp.util.email_formatting import email_format
from parkingApp.models import Parking, ParkingLot
from parkingAuth.models import parkingAuth, ParkingHistory
from django.utils import timezone
from .shared_frame import latest_processed_frame
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# initialization: 
model = ModelManager() # המודלים שיצרנו: מכוניות, לוחיות ומספרים
vehicle = [0, 1] # קלאסים של כלי רכב, 0 - מכוניתת 1 - אופנוע

cap = cv2.VideoCapture('./parkingApp/images/parkingVideo.mp4')
parking_lot_name = 'SCE College' # שם החניון הנסרק

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
saved_check_waiting = {}

# פונקציה לבדיקה אם יש רכב בכל החניות בחניון
# אם יש רכב בחניה מסוימת אנחנו מעדכנים את מצב החנייה: מעדכן רק תפוסה או פנויה         
import traceback

def parking_prediction(img):
    try:
        updated_parkings = []
        parking_queryset = Parking.objects.filter(parking_lot__name=parking_lot_name).select_related('parking_lot')

        for parking in parking_queryset:
            try:
                image = crop_image_by_points(img, parking.coords)
                print(f"\n==================== Processing parking ID: {parking.id} ====================")
                vehicle_predictions = model.free_or_occupied_prediction(image)
                detected_classes = vehicle_predictions[0] if vehicle_predictions else [] 
                detected = any(cls in vehicle for cls in detected_classes)
                park_id = parking.id
                print(f"Current state: {'Occupied' if parking.occupied else 'Free'}")

                # ---- Check if parking state changed ----
                if detected != parking.occupied: 
                    print(f"State change detected for parking ID: {park_id}")
                    if not detected and parking.occupied: 
                        if park_id not in detect_validation_map:
                            detect_validation_map[park_id] = 1
                        else:
                            detect_validation_map[park_id] += 1

                        if detect_validation_map[park_id] >= 3:
                            print(f"Parking {park_id} is now free. Resetting status.")
                            parking.occupied = False
                            parking.unauthorized_parking = False
                            parking.unauthorized_notification_sent = False
                            if parking.driver:
                                sendEmailToUser(parking.driver, "forgot")
                                parking.driver = None
                                parking.save()
                            else:
                                updated_parkings.append(parking)
                            detect_validation_map[park_id] = 0

                    else:
                        parking.occupied = True
                        print(f"Parking {park_id} now occupied.")

                        if parking.is_saved:
                            print(f"{park_id} changed to saved and occupied")
                            updated_parkings.append(parking)
                        elif not parking.driver and not parking.is_saved and not parking.unauthorized_notification_sent:
                            parking.unauthorized_parking = True
                            owner = parking.parking_lot.owner.first()
                            if owner:
                                sendEmailToUser(owner, "unknown_car", pid=park_id)
                                parking.unauthorized_notification_sent = True
                            updated_parkings.append(parking)

                elif detected == parking.occupied:
                    print(f"No state change for parking {park_id}")
                    if parking.occupied and parking.unauthorized_parking and not parking.unauthorized_notification_sent:
                        if park_id not in check_occupancy_map:
                            check_occupancy_map[park_id] = 1
                        else:
                            check_occupancy_map[park_id] += 1

                        if check_occupancy_map[park_id] >= 2:
                            if parking.driver:
                                last_parked = parking.driver
                                owner = parking.parking_lot.owner.all()
                                if owner:
                                    sendEmailToUser(owner[0], "admin_unknown", license_number=last_parked.license_number, phone_number=last_parked.phone_number, pid=park_id)
                                    parking.unauthorized_notification_sent = True
                                parking.driver = None
                                parking.unauthorized_parking = False
                                parking.save()

                            else:
                                matched_user = match_license_plate_to_user(image)
                                owner = parking.parking_lot.owner.first()
                                if matched_user:
                                    parking.driver = matched_user
                                    parking.unauthorized_parking = False
                                    parking.unauthorized_notification_sent = True
                                    parking.save()
                                    sendEmailToUser(matched_user, "wrong_park", pid=park_id)
                                else:
                                    if not parking.unauthorized_notification_sent and owner:
                                        sendEmailToUser(owner, "unknown_car", pid=park_id)
                                        parking.unauthorized_notification_sent = True
                                        print("found unknown car without driver")
                                        parking.save()
                            check_occupancy_map[park_id] = 0

                    detect_validation_map[parking.id] = 0

            except Exception as e:
                print(f"Error processing parking ID {parking.id}: {e}")
                print(traceback.format_exc())

        if updated_parkings:
            print(f"\nUpdating {len(updated_parkings)} parking records.")
            Parking.objects.bulk_update(updated_parkings, ['occupied', 'unauthorized_parking', 'unauthorized_notification_sent'])

    except Exception as e:
        print("Error in parking_prediction function:", e)
        print(traceback.format_exc())

# פונקציה שמבצעת את הסריקה של כל החניות, ומחזירה את מספר החניות התפוסות ומספר החניות הפנויות
# הפונקציה שמבצעת את הסריקה של כל החניות, ומחזירה את מספר החניות הפנויות, התפוסות והשמורות
def liveParkingDetection(img):
    try:
        parking_prediction(img)  # עדכון מצב החנייה בחניון
    except:
        print("error in prediction!")
    parking_queryset = Parking.objects.filter(parking_lot__name=parking_lot_name)

    free = parking_queryset.filter(occupied=False, is_saved=False).count()
    saved = parking_queryset.filter(is_saved=True).count()
    occupied = parking_queryset.filter(occupied=True).count()

    return free, saved, occupied



def generate_frames():
    global frame_count, save_count
    try:
        while True:
            success, img = cap.read() 
            if not success:
                break

            if frame_count % frame == 0:  # כל פריים חמישי נעשה סריקה של כל החניות   
                saved_parking = Parking.objects.filter(is_saved=True).all()  # כל החניות השמורות על ידי משתמשים
                for sp in saved_parking:
                    check_parking_status(sp, crop_image_by_points(img, sp.coords))  # בדיקת מצב שמירה וזיהוי רכב
                
                parkingList = Parking.objects.filter(parking_lot__name=parking_lot_name)  # עדכון רשימת חניות מה־DB

                # סריקה של החניון, קבלת מצב כולל
                free_spaces, saved_spaces, occupied_spaces = liveParkingDetection(img)
                frame_count = 0

            for parking in parkingList:
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

            # ציור הטקסט על המסך
            cv2.putText(img, f"Free: {free_spaces}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, f"Saved: {saved_spaces}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(img, f"Occupied: {occupied_spaces}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            latest_processed_frame[0] = img.copy()
            frame_count += 1

    except Exception as e:
        print(f"Unexpected error in generate_frames: {e}")

    finally:
        print("Releasing video capture and cleaning up...")
        cap.release()
        cv2.destroyAllWindows()


# הפונקציה שבודקת את סטטוס החניות השמורות, האם הרכב ששמר את החנייה הגיע או לא
def check_parking_status(parking, park_img):
    print(f"\n============== Checking parking status for parking ID: {parking.id} ==============")

    # אם החנייה שמורה ולא תפוסה - צריך לבדוק שהנהג לא מאחר
    try:
        if not parking.occupied: 
            print("Parking is not occupied. Checking reservation status...")
            if parking.is_saved and parking.reserved_until < timezone.now():
                print("Reservation expired. Sending email to user and updating status.")
                sendEmailToUser(parking.driver, "late")
                driver = parking.driver
                history = ParkingHistory.objects.filter(driver=driver, parking=parking.id, end_time__isnull=True).first()
                if history:
                    history.end_time = timezone.now()
                    history.save()
                    print("Updated parking history.")

                parking.is_saved = False
                parking.driver = None
                parking.save()
                print("Reservation cleared. Parking is now free.")
    except Exception as e:
        print(f"Error while checking reservation expiration: {e}")

    # אם החנייה שמורה ותפוסה - זה אומר שהרכב הגיע בזמן שלו, צריך לוודא שהוא באמת הוא        
    try:
        if parking.occupied:
            print(f"Parking {parking.id} is occupied. Validating saved driver.")
            if parking.id not in saved_check_waiting:
                saved_check_waiting[parking.id] = 1
            else:
                saved_check_waiting[parking.id] += 1
            
            print(f"Check count for parking {parking.id}: {saved_check_waiting[parking.id]}")

            if saved_check_waiting[parking.id] >= 2 and parking.driver:
                print("Performing driver validation.")
                parking.is_saved = False
                parking.save()
                print("Reservation status cleared for this parking.")

                actual_plate = parking.driver.license_number
                print(f"Expected license plate: {actual_plate}")
                
                try:
                    predicted_plate = model.license_plate_prediction(park_img)
                    if predicted_plate:
                        print("Detected a license plate in the image.")
                        predicted_number = model.license_number_prediction(crop_image_by_points(park_img, predicted_plate[1]))
                        
                        if predicted_number:
                            predicted_plate_number = predicted_number[1]
                            print(f"Predicted license plate number: {predicted_plate_number}")

                            similarity = 1 - Levenshtein.distance(
                                actual_plate, predicted_plate_number
                            ) / max(len(actual_plate), len(predicted_plate_number))
                            print(f"Similarity between actual and predicted plates: {similarity:.2f}")

                            if similarity >= 0.5:
                                sendEmailToUser(parking.driver, "arrived")
                                parking.unauthorized_parking = False
                                parking.unauthorized_notification_sent = True
                                print("Similarity above 0.5 - Driver is considered as arrived.")
                                parking.save()
                            else:
                                sendEmailToUser(parking.driver, "taken")
                                parking.unauthorized_notification_sent = True
                                print("Low similarity - Unauthorized driver detected.")
                                parking.save()
                        else:
                            print("Failed to detect license number. Sending 'undefined' email.")
                            sendEmailToUser(parking.driver, "undefined")

                    else:
                        print("No license plate detected. Sending 'undefined' email.")
                        sendEmailToUser(parking.driver, "undefined")
                
                except Exception as e:
                    print(f"Error in license plate detection: {e}")

            saved_check_waiting[parking.id] = 0

    except Exception as e:
        print(f"Error in validating parked vehicle: {e}")

            

# פונקציה ששולחת מייל למשתמש
def sendEmailToUser(user, status, **kwargs):
    try:
        if status == "admin_unknown":
            email_content = email_format(status, user_name=user.first_name, userid=user.id, phone_number=kwargs['phone_number'], license_number=kwargs['license_number'], pid=kwargs['pid']) 
        elif status == "unknown_car":
            email_content = email_format(status, user_name=user.first_name, userid=user.id ,pid=kwargs['pid']) 
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
    

def match_license_plate_to_user(image):
    try:
        predicted_plate = model.license_plate_prediction(image)
        if predicted_plate is None:
            return None

        predicted_number_result = model.license_number_prediction(crop_image_by_points(image, predicted_plate[1]))
        if predicted_number_result is None:
            return None

        predicted_number = predicted_number_result[1]
        registered_user = parkingAuth.objects.filter(license_number=predicted_number).first()

        return registered_user

    except Exception as e:
        print(f"Not Found!")
        return None
    

def run():
    generate_frames()

