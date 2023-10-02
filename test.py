import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model

facedetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
font = cv2.FONT_HERSHEY_COMPLEX

model = load_model('model/my_model.keras')

# Mapeamento de classe para nome de usuário com base nas pastas
class_to_user = {}
user_folders = os.listdir('images')  # Substitua pelo caminho correto
for i, user_folder in enumerate(user_folders):
    class_to_user[i] = user_folder

while True:
    success, imgOriginal = cap.read()
    faces = facedetect.detectMultiScale(imgOriginal, 1.3, 5)
    for x, y, w, h in faces:
        crop_img = imgOriginal[y:y+h, x:x+w]
        
        # Redimensione a imagem para as dimensões esperadas (128x128 pixels)
        img = cv2.resize(crop_img, (128, 128))
        
        img = img.reshape(1, 128, 128, 3)  # Redimensione também a forma da imagem
        
        prediction = model.predict(img)
        classIndex = np.argmax(prediction)
        probabilityValue = np.amax(prediction)
        
        user_name = class_to_user.get(classIndex, "Não Reconhecido")
        
        cv2.rectangle(imgOriginal, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.rectangle(imgOriginal, (x, y-40), (x+w, y), (0, 255, 0), -2)
        cv2.putText(imgOriginal, user_name, (x, y-10), font, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(imgOriginal, str(round(probabilityValue*100, 2)) + "%", (180, 75), font, 0.75, (255, 0, 0), 2, cv2.LINE_AA)
    
    cv2.imshow("Result", imgOriginal)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
