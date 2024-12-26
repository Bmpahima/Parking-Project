import cv2
import pickle
import os
import numpy as np
import math

# from model import make_prediction

# שומר את התמונות 
save_dir = 'parking_images'

# אם התיקיה לא קיימת - תיצור אותה
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# לפתוח קובץ פיקל ששומר את הנקודות
try:
    with open('carposition.pkl', 'rb') as f:
        positionList = pickle.load(f)
except:
    positionList = []

current_pos = [] 

def get_next_id():
    return max([pos['id'] for pos in positionList]) + 1 if positionList else 0

# פונקציה לחישוב המיקום של הטקסט עבור כל חנייה
def mid_point(point1, point2):
    mid_x = ((point1[0] + point2[0]) / 2) - 24
    mid_y = ((point1[1] + point2[1]) / 2)
    return (int(mid_x), int(mid_y))  # המרת ערכים לשלמים

# פונקציה לשמירת התמונות
def save_cropped_img(img, points, id):
    # שמירת הנקודות המערך של נאמפיי כדי שיתאימו בפורמט לפונקציה של שינוי הפרספקטיבה
    src_points = np.array(points, dtype=np.float32)

    # Calculate the width and height of the image
    img_width = math.floor(math.dist(points[0], points[1]))
    img_height = math.floor(math.dist(points[1], points[2]))
    print(img_width, img_height)

    dst_points = np.array([[0, 0], [img_width, 0], [img_width, img_height], [0, img_height]], dtype=np.float32)

    # מקבל את המטריצה של הפרספקטיבה
    matrix = cv2.getPerspectiveTransform(src_points, dst_points) # התאמת פרספקטיבה

    # משנה את הפרספקטיבה של התמונה
    cropped_img = cv2.warpPerspective(img, matrix, (img_width, img_height)) # צריך את התמונה אחרי שינוי הפרספקטיבה לצורך זיהוי אם יש שם מכונית או לא

    # שמירת התמונה
    save_path = os.path.join(save_dir, f'parking_no{id}.png')
    cv2.imwrite(save_path, cropped_img)
    print(f'Saved cropped image: {save_path}')


def mouseclick(events, x, y, flags, params):
    global current_pos

    if events == cv2.EVENT_LBUTTONDOWN:
        current_pos.append((x, y))
        print(f'Point added: {x, y}')

        # אם נבחרו 4 נקודות ישמור את הנקודות ויציג את החנייה
        if len(current_pos) == 4:
            positionList.append({
                "id": get_next_id(),
                "points": current_pos,
                "occupied": False
            })
            save_cropped_img(cv2.resize(cv2.imread('parking.png'), (1280, 720)), current_pos, (get_next_id() - 1)) # שמירת התמונה של החנייה
            current_pos = []  # בחירת נקודו מחודשת

    # אם נלחץ על הכפתור הימני זה ימחק את החנייה
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(positionList):
            # Assuming you want to check if (x, y) is inside any saved polygon (simplification needed)
            if cv2.pointPolygonTest(np.array(pos['points'], dtype=np.int32), (x, y), False) >= 0:
                print(f'Removed region: {pos}')
                positionList.pop(i)
                if os.path.exists(save_dir + f'/parking_no{pos["id"]}.png'):
                    os.remove(save_dir + f'/parking_no{pos["id"]}.png')
                break

    # שומר את הנקודות בקובץ פיקל
    with open('carposition.pkl', 'wb') as f:
        pickle.dump(positionList, f)

def initial_parking_mark():
    while True:
        image = cv2.imread('parking.png')

        # כל חנייה מיוצגת על ידי 4 נקודות 
        # מצייר את הצורות של החניות לפי הנקודות
        for pos in positionList:
            pts = np.array(pos['points'], np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(img=image, 
                        text=f"ID: {pos['id']}", 
                        org=mid_point(pos['points'][0], pos['points'][2]), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=0.7, 
                        color=(0, 0, 255), 
                        thickness=2)

        # כל נקודה שנבחרה לחנייה תסומן בעיגול
        for pt in current_pos:
            cv2.circle(image, pt, radius=5, color=(0, 255, 0), thickness=-1)

        # מציג את התמונה ומפעיל את הevent listener
        cv2.imshow("Image", image)
        cv2.setMouseCallback("Image", mouseclick)

        # אם נלחץ על התו q זה יסיים את התוכנית
        k = cv2.waitKey(1)
        if k == ord('q'):
            break

        # סוגר את כל החלונות
    cv2.destroyAllWindows()


initial_parking_mark()
# def initial_prediction():
#     for pos in positionList:
#         # פונקציה שמחזירה אם יש מכונית או לא
#         prediction = make_prediction(f'parking_images/parking_no{pos["id"]}.png')
#         pos['occupied'] = prediction == 'Car' 

