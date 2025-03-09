# import cv2
# import numpy as np

# # טוען את הסרטון
# cap = cv2.VideoCapture(r'C:\Users\MeirHaimov\Downloads\IMG_6572.mov')

# # מגדיר את כותב הווידאו (שומר את הווידאו החדש) עם קידוד MJPEG
# fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # קידוד MJPEG
# out = cv2.VideoWriter('sharpened_video.avi', fourcc, cap.get(cv2.CAP_PROP_FPS),
#                       (int(cap.get(3)), int(cap.get(4))))

# # פילטר חידוד
# kernel = np.array([[0, -1, 0], 
#                    [-1, 5, -1], 
#                    [0, -1, 0]])

# # סופרים את מספר הפריימים
# frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# processed_frames = 0

# # עיבוד הווידאו עם עדכון התקדמות
# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # החלת פילטר חידוד
#     sharpened = cv2.filter2D(frame, -1, kernel)

#     # כתיבה לקובץ
#     out.write(sharpened)

#     # עדכון התקדמות
#     processed_frames += 1
#     print(f"Processing frame {processed_frames}/{frame_count} ({(processed_frames/frame_count)*100:.2f}%)", end='\r')

# cap.release()
# out.release()
# print("\n✅ עיבוד הסרטון הסתיים! הקובץ נשמר כ- sharpened_video.avi")
