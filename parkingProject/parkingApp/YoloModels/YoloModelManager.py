from ultralytics import YOLO
import math

class ModelManager:
    """
    A manager class for handling YOLO-based object detection models 
    for vehicle presence detection, license plate localization, 
    and license plate number recognition.

    Attributes:
        vehicle_model (YOLO): YOLO model for detecting vehicles.
        license_plate_model (YOLO): YOLO model for detecting license plates.
        license_number_model (YOLO): YOLO model for detecting license plate characters.
        classes (tuple): Tuple of class names for each model.
    """

    def __init__(self, vehicle_model_path="./parkingApp/YoloModels/VehiclesModel.pt",
                 lp_model_path="./parkingApp/YoloModels/LicensePlateModel.pt",
                 numbers_models_path="./parkingApp/YoloModels/LicensePlateNumModel.pt"):
        """
        Initializes all three YOLO models for vehicle, license plate, and character detection.

        Args:
            vehicle_model_path (str): Path to the YOLO model for detecting vehicles.
            lp_model_path (str): Path to the YOLO model for detecting license plates.
            numbers_models_path (str): Path to the YOLO model for detecting license plate numbers.
        """
        self.vehicle_model = YOLO(vehicle_model_path, verbose=False)
        self.license_plate_model = YOLO(lp_model_path, verbose=False)
        self.license_number_model = YOLO(numbers_models_path, verbose=False)
        self.classes = (
            self.vehicle_model.names,
            self.license_plate_model.names,
            self.license_number_model.names
        )

    def free_or_occupied_prediction(self, img, conf=0.55):
        """
        Predicts whether a parking spot is free or occupied based on vehicle detection.

        Args:
            img (ndarray): The input image.
            conf (float): Confidence threshold for detection.

        Returns:
            tuple or None: (classes, bounding box points, confidence scores)
                           or None if no valid detections.
        """
        if img is None:
            return None
        
        predictions = self.vehicle_model.predict(img, conf=conf, verbose=False)
        if not predictions or not predictions[0].boxes:
            return None

        boxes = predictions[0].boxes
        classes = boxes.cls.cpu().tolist()
        x1, y1, x2, y2 = predictions[0].boxes.xyxy.tolist()[0]
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        confidence = boxes.conf.tolist()

        return (classes, points, confidence)

    def license_plate_prediction(self, img, conf=0.45):
        """
        Detects a license plate in the given image.

        Args:
            img (ndarray): The input image.
            conf (float): Confidence threshold for detection.

        Returns:
            tuple or None: (classes, bounding box points, confidence scores)
                           or None if no plate is detected.
        """
        if img is None:
            return None

        predictions = self.license_plate_model.predict(img, conf=conf, verbose=False)
        if not predictions or not predictions[0].boxes:
            return None

        boxes = predictions[0].boxes
        classes = boxes.cls.cpu().tolist()
        x1, y1, x2, y2 = predictions[0].boxes.xyxy.tolist()[0]
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        confidence = boxes.conf.tolist()

        return (classes, points, confidence)

    def license_number_prediction(self, img, conf=0.55, is_car=True):
        """
        Detects and returns the license plate number as a string.

        Args:
            img (ndarray): Cropped image of the license plate.
            conf (float): Confidence threshold.
            is_car (bool): Whether the plate is from a car (True) or motorcycle (False).

        Returns:
            tuple or None: (detected classes, license number string, confidence scores)
                           or None if no valid prediction.
        """

        def lisence_number_extractor(numbers_predictions):
            """
            Helper function to sort and extract the number from predictions.
            """
            if not numbers_predictions:
                return None

            sorted_predictions = sorted(numbers_predictions, key=lambda num: num[1])
            return ''.join(str(cls[0]) for cls in sorted_predictions)

        predictions = self.license_number_model.predict(img, conf=conf, verbose=False)
        if not predictions or not predictions[0].boxes:
            return None

        boxes = predictions[0].boxes
        classes = boxes.cls.cpu().tolist()
        
        if len(classes) not in [4, 5, 6, 7, 8]:
            return None
        
        for cls in classes:
            if not isinstance(cls, (int, float)) or math.isnan(cls):
                return None

        numbers_x_axis = []

        if is_car:
            for i in range(len(classes)):
                cls = int(boxes.cls[i])
                x_coord = float(boxes.xyxy[i][2])
                numbers_x_axis.append((cls, x_coord))
        else:
            for i in range(len(classes)):
                cls = int(boxes.cls[i])
                y_coord = float(boxes.xyxy[i][3])
                x_coord = float(boxes.xyxy[i][2])
                numbers_x_axis.append((cls, x_coord, y_coord))

            numbers_x_axis = sorted(numbers_x_axis, key=lambda num: num[2])
            first_row = numbers_x_axis[:5]
            second_row = numbers_x_axis[5:]
            first_row = sorted(first_row, key=lambda num: num[1])
            second_row = sorted(second_row, key=lambda num: num[1])
            numbers_x_axis = first_row + second_row

        if is_car:
            license_number_text = lisence_number_extractor(numbers_x_axis) or "not found"
        else:
            license_number_text = ''.join(str(x[0]) for x in numbers_x_axis)

        print(license_number_text)
        confidence = boxes.conf.tolist()

        return (classes, license_number_text, confidence)
