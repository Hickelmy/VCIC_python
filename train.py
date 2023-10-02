import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# Caminho para o haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Função para extrair rostos das imagens
def extract_faces(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    
    face_images = []
    for (x, y, w, h) in faces:
        face = img[y:y+h, x:x+w]
        face_images.append(face)
    
    return face_images

# Diretório raiz onde estão as pastas de cada usuário
root_dir = 'images'

# Lista de pastas de usuários (cada pasta contendo 500 imagens)
user_folders = os.listdir(root_dir)

# Inicialize listas para armazenar imagens e rótulos
X = []  # Imagens
y = []  # Rótulos (identificador de usuário)

# Itere sobre as pastas dos usuários
for user_id, user_folder in enumerate(user_folders):
    user_path = os.path.join(root_dir, user_folder)
    image_files = os.listdir(user_path)
    
    # Itere sobre as imagens do usuário
    for image_file in image_files:
        image_path = os.path.join(user_path, image_file)
        faces = extract_faces(image_path)
        
        for face in faces:
            # Redimensione a imagem para um tamanho adequado para seu modelo
            # (por exemplo, 128x128 pixels)
            face = cv2.resize(face, (128, 128))
            
            X.append(face)
            y.append(user_id)

# Transforme as listas em matrizes NumPy
X = np.array(X)
y = np.array(y)

# Construa e treine um modelo de aprendizado profundo
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(len(user_folders), activation='softmax'))

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(X, y, epochs=10)  # Ajuste o número de épocas conforme necessário

# Crie uma pasta chamada 'model' se ela não existir
if not os.path.exists('model'):
    os.makedirs('model')

# # Salve o modelo treinado no formato HDF5
# model.save('model/facial_recognition_model.h5')

# Salvar o modelo em formato Keras nativo
model.save('model/my_model.keras')

