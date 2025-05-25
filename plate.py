from ultralytics import YOLO
import cv2
import numpy as np


model = YOLO('LicensePlateNumModel.pt')

def plate_predict(path):
    """
    Detects and returns the license plate number from an image using a YOLO model.

    Args:
        path (str): Path to the image file containing the license plate.

    Returns:
        str: A string representing the sorted license plate number, or "not found" if
             the prediction is invalid (not 7 or 8 characters).

    Behavior:
        - Loads the image using OpenCV.
        - Uses the YOLO model to detect characters on the plate.
        - Sorts characters based on their X-position (left to right).
        - Assembles and prints the license number.
        - Returns "not found" if the number of detected characters is not 7 or 8.
    """
    predictions = []

    img = cv2.imread(path)
    results = model.predict(source=img, conf=0.55)
    if results:
        boxes = results[0].boxes
        for i in range(len(boxes.cls)):
            cls = int(boxes.cls[i])  
            top_right = float(boxes.xyxy[i][2]) 
            predictions.append((cls, top_right))
    
    if len(predictions) not in [7, 8]:
        return "not found"
    for prediction in predictions:
        print(prediction)

    sorted_predictions = sorted(predictions, key=lambda num: num[1])
    license_number_text = ''
    for cls in sorted_predictions:
        license_number_text += str(cls[0])
    
    print(license_number_text)


if __name__ == "__main__":
    plate_predict('p6.png')