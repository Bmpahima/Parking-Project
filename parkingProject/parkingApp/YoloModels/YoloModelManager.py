from ultralytics import YOLO
import math

class ModelManager ():
    def __init__(self, vehicle_model_path="./parkingApp/YoloModels/VehiclesModel.pt",
                 lp_model_path="./parkingApp/YoloModels/LicensePlateModel.pt",
                 numbers_models_path="./parkingApp/YoloModels/LicensePlateNumModel.pt"):
        self.vehicle_model = YOLO(vehicle_model_path, verbose=False)
        self.license_plate_model = YOLO(lp_model_path,  verbose=False)
        self.license_number_model = YOLO(numbers_models_path,  verbose=False)
        self.classes = (self.vehicle_model.names, self.license_plate_model.names, self.license_number_model.names)

    def free_or_occupied_prediction(self, img, conf=0.55):
        if img is None:
            return None
        
        predictions = self.vehicle_model.predict(img, conf=conf, verbose=False)

        if not predictions:
            return None

        boxes = predictions[0].boxes

        if len(boxes) == 0:
            return None 

        classes = boxes.cls.cpu().tolist()
        x1, y1, x2, y2 = predictions[0].boxes.xyxy.tolist()[0]
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        confidence = boxes.conf.tolist()

        results = (
            classes,
            points,
            confidence
        )

        return results
    
    def license_plate_prediction(self, img, conf=0.45):
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

        results = (
            classes,
            points,
            confidence
        )

        return results
    

    def license_number_prediction(self, img, conf=0.55, is_car=True):

        def lisence_number_extractor(numbers_predictions):
            if not numbers_predictions:
                return None

            sorted_predictions = sorted(numbers_predictions, key=lambda num: num[1])
            license_number_text = ''.join(str(cls[0]) for cls in sorted_predictions)
            
            return license_number_text


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

            numbers_x_axis = []
            numbers_x_axis = first_row + second_row
        
        if is_car:
            license_number_text = lisence_number_extractor(numbers_x_axis) if lisence_number_extractor(numbers_x_axis) else "not found"
        else:
            license_number_text = ''.join(str(x[0]) for x in numbers_x_axis)

        print(license_number_text)
        confidence = boxes.conf.tolist()

        results = (
            classes,
            license_number_text,
            confidence
        )

        return results
    
        
    
    

