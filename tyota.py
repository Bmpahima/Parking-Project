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