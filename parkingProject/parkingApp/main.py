# daphne -b 0.0.0.0 -p 8000 parkingProject.asgi:application
"""
This script handles real-time parking management using a Raspberry Pi camera and YOLO object detection.
It includes:
- Camera and model initialization
- Parking space scanning
- Occupancy state updates
- Email notifications
- Frame streaming via WebSocket
""" 
import os
import django
import Levenshtein
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkingProject.settings')
from django.core.mail import send_mail
from django.conf import settings
django.setup()
import cv2
import numpy as np
from parkingApp.YoloModels.YoloModelManager import ModelManager
from parkingApp.util.image_processing import crop_image_by_points, set_text_position
from parkingApp.util.email_formatting import email_format
from parkingApp.models import Parking, ParkingLot
from parkingAuth.models import parkingAuth
from django.utils import timezone
import time
from picamera2 import Picamera2
from channels.layers import get_channel_layer
import json
import asyncio




# Initialize the YOLO model manager (vehicles, plates, numbers)

model = ModelManager()

# Define vehicle classes used in detection (0 = car, 1 = motorcycle)

vehicle = [0, 1] 

# Initialize and configure PiCamera
picam2 = Picamera2()
picam2.configure(
    picam2.create_video_configuration(
        main={"format": "BGR888", "size": (1280, 720)},
        controls={"FrameRate": 10},
        display=None
    )
)

print("[DEBUG] Camera configured.")
picam2.start()
print("[DEBUG] Camera started.")
time.sleep(1) 
# Define parking lot Name assigned to this device
parking_lot_name = 'raspi'
print("[DEBUG] Testing camera capture...")

test_frame = picam2.capture_array()
if test_frame is None:
    print("[ERROR] No frame captured in test.")
else:
    print("[DEBUG] Test frame captured successfully.")


# Define scanning frequency (every 5 * 10 frames)
fps = 30
current_frame = int(10 * 5)
frame_count = 0

# Load all parkings from current parking lot
queryset = ParkingLot.objects.filter(name=parking_lot_name)
if queryset.exists():
    parkingList = queryset.first().parkings.all() #brings back the parking spots from the parking lot
else:
    print(f"No parking lot found with name: {parking_lot_name}")
    parkingList = []

detect_validation_map = {} #make sure that the parking spot is avalible
check_occupancy_map = {}
saved_check_waiting = {}
occupancy_flag_check = {}


def parking_prediction(img):
    """
    Predicts occupancy of all parking spots in the lot using a detection model.
    Updates their state accordingly and sends notifications if unauthorized usage is detected.

    Args:
        img (np.ndarray): Captured frame from the camera.
""" 
    updated_parkings = []
    parking_queryset = Parking.objects.filter(parking_lot__name=parking_lot_name).select_related('parking_lot')

    for parking in parking_queryset:
        image = crop_image_by_points(img, parking.coords) 

        vehicle_predictions = model.free_or_occupied_prediction(image)
        detected_classes = vehicle_predictions[0] if vehicle_predictions else [] 
        detected = any(cls in vehicle for cls in detected_classes)
        park_id = parking.id
        
        #Check if there is some change of the state of the parking spot
        if detected != parking.occupied: 
            if not detected and parking.occupied: #was car, and now there is no car
                #check 3 times if the parking spot is really avaliable - to make sure.
                if park_id not in detect_validation_map: 
                    detect_validation_map[park_id] = 1
                else:
                    detect_validation_map[park_id] += 1
            
                if detect_validation_map[park_id] >= 4:
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


            else:#before, wasnt car and now there is a car
                if park_id not in occupancy_flag_check: 
                    occupancy_flag_check[park_id] = 1
                else:
                    occupancy_flag_check[park_id] += 1
            
                if occupancy_flag_check[park_id] >= 4:
                    parking.occupied = True
                    if parking.is_saved:
                        print(f"{park_id} changed to saved and occupied")
                        updated_parkings.append(parking)
                        continue
                    elif not parking.driver and not parking.is_saved and not parking.unauthorized_notification_sent:
                        parking.unauthorized_parking = True
                        owner = parking.parking_lot.owner.first()
                        if owner:
                            sendEmailToUser(owner, "unknown_car", pid=park_id)
                            parking.unauthorized_notification_sent = True
                            print("now there is car")
                        updated_parkings.append(parking)
                    occupancy_flag_check[park_id] = 0

        #check if there is no change of the state of the parking spot
        elif detected == parking.occupied:
            #if the spot is occuiped but the driver is unknown
            if parking.occupied and parking.unauthorized_parking and not parking.unauthorized_notification_sent:
                if park_id not in check_occupancy_map: 
                    check_occupancy_map[park_id] = 1
                else:
                    check_occupancy_map[park_id] += 1 
                #if after 20 checks the parking spot still ocupied and the car has no access - we send mail to the admin.
                if check_occupancy_map[park_id] >= 6: 
                    if parking.driver: #the driver is delayed for exit the parking lot
                        last_parked = parking.driver
                        owner = parking.parking_lot.owner.all()

                        if owner:
                            sendEmailToUser(owner[0], "admin_unknown", license_number=last_parked.license_number, phone_number=last_parked.phone_number, pid=park_id)
                            parking.unauthorized_notification_sent = True 
                            print("found onknown car w driver")
                        parking.driver = None
                        parking.unauthorized_parking = False
                        parking.save()
                    
                    else:  #parking spot is occuiped and we dont have info about the driver, sending mail to admin of the parking lot
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
                                print("found onknown car without driver")
                                parking.save()
                    check_occupancy_map[park_id] = 0

            detect_validation_map[parking.id] = 0

    if updated_parkings:#Update only changed parking spots          
        Parking.objects.bulk_update(updated_parkings, ['occupied', 'unauthorized_parking', 'unauthorized_notification_sent'])



def liveParkingDetection(img):
    """
    Detects live parking status for the entire lot and returns a summary count.

    Args:
        img (np.ndarray): Captured image.

    Returns:
        tuple: Number of (avaliable, saved, occupied) parking spots.
    """
    try:
        parking_prediction(img)
    except:
        print("error in prediction!")
    parking_queryset = Parking.objects.filter(parking_lot__name=parking_lot_name)

    free = parking_queryset.filter(occupied=False, is_saved=False).count()
    saved = parking_queryset.filter(is_saved=True).count()
    occupied = parking_queryset.filter(occupied=True).count()

    return free, saved, occupied

import base64

async def send_frame_to_ws(frame):
    """
    Sends a single encoded video frame to the video stream WebSocket group.
    only the manager of the parking lot can see the live stream.
    Args:
        frame (np.ndarray): Frame to be sent.
    """
    ...
    print("sending....")
    _, buffer = cv2.imencode('.jpg', frame)
    if buffer is None:
        print("Failed to encode frame")
        return

    frame_base64 = base64.b64encode(buffer).decode('utf-8')  
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "video_stream",  
        {
            "type": "receive",  
            "text_data": json.dumps({"frame": frame_base64})
        }
    )
    print("frame sent...")



def generate_frames():
    """
    Continuously captures video frames from the PiCamera, scans for parking space occupancy,
    updates the parking database, overlays visual indicators on the frames, and sends them
    through WebSocket for real-time streaming.

    Workflow:
        1. Capture a frame.
        2. Every Nth frame, detect vehicles in all saved/reserved parking spots.
        3. Run overall detection across the entire lot.
        4. Draw colored boundaries over each parking spot:
            - Red for occupied
            - Blue for saved
            - Green for free
        5. Display summary stats (counts).
        6. Stream the frame to frontend via WebSocket.
        7. Repeat until user presses 'q'.

    Global:
        frame_count (int): Tracks number of frames processed for periodic scanning.

    Raises:
        Handles all exceptions internally with logging; never throws.
    """
    global frame_count, save_count

    while True:
        try:
            frame = picam2.capture_array()
            if frame is None:
                print("[ERROR] No frame captured.")
                continue
            # show the frame
            # cv2.imshow("Parking Detection", frame)
            # print("[DEBUG] Frame displayed.")

        except Exception as e:
            print(f"[ERROR] Failed to capture frame: {str(e)}")
            continue  #go to the next attempt

        # Test: Will we scan all parking lots (every 5 frames)
        if frame_count % current_frame == 0:
            try:
                saved_parking = Parking.objects.filter(is_saved=True).all()
                for sp in saved_parking:
                    check_parking_status(sp, crop_image_by_points(frame, sp.coords))
                
                parkingList = Parking.objects.filter(parking_lot__name=parking_lot_name)
                free_spaces, saved_spaces, occupied_spaces = liveParkingDetection(frame)
                frame_count = 0
            except Exception as e:
                print(f"[ERROR] Error scanning parking spots: {str(e)}")
        else:
            print(f"[DEBUG] Frame count: {frame_count}")

        # drawing the bounding spots and status
        try:
            for parking in parkingList:
                pts = np.array(parking.coords, np.int32).reshape((-1, 1, 2))
                color = (0, 0, 255) if parking.occupied else ((255, 0, 0) if parking.is_saved else (0, 255, 0))
                cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
                cv2.putText(frame, f"ID: {parking.id}",
                            org=set_text_position(parking.coords[0], parking.coords[2]),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.7,
                            color=(0, 0, 255),
                            thickness=2)

            #draw status 
            cv2.putText(frame, f"Free: {free_spaces}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Saved: {saved_spaces}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, f"Occupied: {occupied_spaces}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        except Exception as e:
            print(f"[ERROR] Failed to annotate frame: {str(e)}")

        # send the frames via websocket
        try:
            asyncio.run(send_frame_to_ws(frame))
        except Exception as e:
            print(f"[ERROR] Failed to send frame to WebSocket: {str(e)}")

        # check for exit from the loop 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    #Clean resources
    picam2.stop()
    cv2.destroyAllWindows()
    print("[DEBUG] Camera stopped and resources released.")




# הפונקציה שבודקת את סטטוס החניות השמורות, האם הרכב ששמר את החנייה הגיע או לא
def check_parking_status(parking, park_img):
    """
    Verifies whether the reserved parking spot is used correctly by the driver or if there
   is a delay or unauthorized vehicle. It handles validation using license plate recognition
    and sends notifications accordingly.

    Logic:
        - If the parking is saved but not occupied:
            - Check if the reservation time has expired.
            - If so, cancel the reservation and notify the driver.

        - If the parking is both saved and occupied:
            - Wait for 2 cycles before proceeding to plate verification.
            - Compare the actual driver license number with the detected plate number.
            - Use Levenshtein distance to allow fuzzy match.
            - If match is strong enough, mark as valid arrival.
            - If not, notify driver about possible misuse.
            - If plate is unreadable, notify as undefined.

    Args:
        parking (Parking): Reserved parking spot instance.
        park_img (np.ndarray): Cropped image of the parking area.
    """
    #if the parking spot is saved and not occupied - we need to check if the car is not late
    if not parking.occupied: 
        if parking.is_saved and parking.reserved_until < timezone.now(): #If the person's time limit has arrived - they are late, so we will cancel saved spot and notify them by email.

            sendEmailToUser(parking.driver, "late")
            parking.is_saved = False #The parking lot is once again unreserved and available to drivers.
            parking.driver = None
            parking.save()        

    #If the parking lot is reserved and occupied - it means the vehicle arrived on time, we need to check if this is really he
    else:
        if parking.id not in saved_check_waiting:
            saved_check_waiting[parking.id] = 1
        else:
            saved_check_waiting[parking.id] += 1
        
        if saved_check_waiting[parking.id] >= 6 and parking.driver:
            parking.is_saved = False #now the parking spot is not saved
            parking.save()
            print("not saved anymore!")

            actual_plate = parking.driver.license_number #the license plate number of the driver
            predicted_plate = model.license_plate_prediction(park_img) #whats the model is recognized
            if predicted_plate is not None:
                print("found a plate!")
                predicted_number = model.license_number_prediction(crop_image_by_points(park_img, predicted_plate[1])) # זיהוי מספר הלוחי עצמה
                if predicted_number is not None:
                    predicted_plate_number = predicted_number[1] #the license plate that the model detacted
                    print(f"number found: {predicted_plate_number}")
                    #Levenshtien distance to check the similarty between the actual license plate number to the predicted number.
                    similarity = 1 - Levenshtein.distance(actual_plate, predicted_plate_number) / max(len(actual_plate), len(predicted_plate_number))
                    print(f"similarity: {similarity}")
                    #if the similarity is higher then 0.5, we recognized the car.
                    if similarity >= 0.5: 
                        sendEmailToUser(parking.driver, "arrived")
                        parking.unauthorized_parking = False
                        parking.unauthorized_notification_sent = True 
                        parking.save()
                        
                    #else, we will send email to the parking lot manager that we didnt recognize the driver.
                    else: 
                        sendEmailToUser(parking.driver, "taken")
                        parking.unauthorized_notification_sent = True
                        parking.save()
                        print("taken")
                else:
                    sendEmailToUser(parking.driver, "undefined")
                    print("undefined1")
            
            else: 
                sendEmailToUser(parking.driver, "undefined")
            saved_check_waiting[parking.id] = 0
            


def sendEmailToUser(user, status, **kwargs):
    """
    Sends a formatted email notification to a user depending on parking status.

    Args:
        user (User): The recipient user.
        status (str): Type of status ('forgot', 'late', 'unknown_car', etc.)
        **kwargs: Additional context for email (e.g. license_number, phone_number).
    """
    try:
        if status == "admin_unknown":
            email_content = email_format(status, user_name=user.first_name, userid=user.id, phone_number=kwargs['phone_number'], license_number=kwargs['license_number'], pid=kwargs['pid']) 
        elif status == "unknown_car":
            email_content = email_format(status, user_name=user.first_name, userid=user.id ,pid=kwargs['pid']) 
        else: email_content = email_format(status, user_name=user.first_name, userid=user.id) 

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
    """
    Matches a detected license plate from an image to a registered user.

    Args:
        image (np.ndarray): The full frame image.

    Returns:
        parkingAuth or None: Matching user or None if no match.
    """
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


print("[DEBUG] main.py loaded.")

def start_parking_loop():
    """
    Starts the main loop responsible for capturing and analyzing frames.
    """
    try:
        generate_frames()
    except Exception as e:
        print(f"[ERROR] Error in main: {str(e)}")

if __name__ == "__main__":
    print("[DEBUG] Starting main process...")
    start_parking_loop()

