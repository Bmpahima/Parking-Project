import cv2
import numpy as np

def set_text_position(point1, point2):
    mid_x = ((point1[0] + point2[0]) / 2) - 24
    mid_y = ((point1[1] + point2[1]) / 2)
    return (int(mid_x), int(mid_y)) 


def crop_image_by_points(img, points):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    points = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)

    masked_img = cv2.bitwise_and(img, img, mask=mask)

    x, y, w, h = cv2.boundingRect(points)
    cropped_img = masked_img[y:y+h, x:x+w]
    return cropped_img


def get_first_frame(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        
        success, frame = cap.read()

        cap.release()
        if not success:
            return None
        
        return frame
 
    except Exception as e:
        print(f"Error in loading video: {e}")
        return None
    

