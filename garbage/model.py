import cv2
import numpy as np
from keras.api import models

model = models.load_model('model.h5')

def make_prediction(image):
    image = cv2.resize(image, (48, 48))
    img = image/255 
    img = np.expand_dims(img, axis = 0) 

    class_predicted = model.predict(img)
    intId = np.argmax(class_predicted[0])
    return 'Car' if intId == 1 else 'No Car'