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