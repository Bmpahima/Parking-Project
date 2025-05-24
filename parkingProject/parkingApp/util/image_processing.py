import cv2
import numpy as np

def set_text_position(point1, point2):
    """
    Calculates a text position between two points for overlaying on an image.

    Args:
        point1 (tuple): The first point (x1, y1) of the bounding box.
        point2 (tuple): The second point (x2, y2) of the bounding box.

    Returns:
        tuple: The (x, y) coordinates representing the midpoint for text display,
               shifted slightly to the left for better visual alignment.
    """

    mid_x = ((point1[0] + point2[0]) / 2) - 24
    mid_y = ((point1[1] + point2[1]) / 2)
    return (int(mid_x), int(mid_y)) 


def crop_image_by_points(img, points):
    """
    Crops an image based on a polygon defined by given points.

    Args:
        img (ndarray): The original image.
        points (list of tuples): A list of (x, y) tuples defining a polygon region.

    Returns:
        ndarray: The cropped portion of the image within the polygon area.
    """

    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    points = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points], 255)

    masked_img = cv2.bitwise_and(img, img, mask=mask)

    x, y, w, h = cv2.boundingRect(points)
    cropped_img = masked_img[y:y+h, x:x+w]
    return cropped_img


def get_first_frame(video_path):
    """
    Extracts and returns the first frame of a video file.

    Args:
        video_path (str): The path to the video file.

    Returns:
        ndarray or None: The first video frame as an image (if successful),
                         or None if the frame could not be read.
    """
    
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
    

