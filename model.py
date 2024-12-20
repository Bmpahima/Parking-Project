import cv2
import numpy as np
from keras.api import models

# טוען את המודל


model = models.load_model('model.h5')

##### נשים לב הפונקציה מקבלת תמונה
def make_prediction(image):
    image = cv2.resize(image, (48, 48))
    img = image/255 # נורמליזציה
    img = np.expand_dims(img, axis = 0) # הרחבת המימד כי ככה המודלים מצפים לקבל את התמונות שלהם כקלט

    class_predicted = model.predict(img)
    intId = np.argmax(class_predicted[0])
    return 'Car' if intId == 1 else 'No Car'