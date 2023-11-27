import customtkinter as ctk
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
from pymongo import MongoClient
import io


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

appWidth, appHeight = 1024, 768


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("PYvision")
        self.geometry(f"{appWidth}x{appHeight}")
        self.capture_count = 0
        self.setup_ui()

    def setup_ui(self):
        central_frame = ctk.CTkFrame(self)
        central_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Progress Label
        self.progressLabel = ctk.CTkLabel(central_frame, text="Progress: 0/500")
        self.progressLabel.grid(
            row=7, column=0, columnspan=4, padx=20, pady=20, sticky="ew"
        )

        # MongoDB Connection
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_client["user_data"]

        # Name Label
        self.nameLabel = ctk.CTkLabel(central_frame, text="Nome")
        self.nameLabel.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Name Entry Field
        self.nameEntry = ctk.CTkEntry(central_frame, placeholder_text="nome...")
        self.nameEntry.grid(
            row=0, column=1, columnspan=3, padx=20, pady=20, sticky="ew"
        )

        # Age Label
        self.ageLabel = ctk.CTkLabel(central_frame, text="Idade")
        self.ageLabel.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        # Age Entry Field
        self.ageEntry = ctk.CTkEntry(central_frame, placeholder_text="34...")
        self.ageEntry.grid(row=1, column=1, columnspan=3, padx=20, pady=20, sticky="ew")

        # Gender Label
        self.genderLabel = ctk.CTkLabel(central_frame, text="Genero")
        self.genderLabel.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        # Gender Radio Buttons
        self.genderVar = tk.StringVar(value="Prefiro não dizer")

        self.maleRadioButton = ctk.CTkRadioButton(
            central_frame, text="Masculino", variable=self.genderVar, value="Masculino"
        )
        self.maleRadioButton.grid(row=2, column=1, padx=20, pady=20, sticky="ew")

        self.femaleRadioButton = ctk.CTkRadioButton(
            central_frame, text="Feminino", variable=self.genderVar, value="Feminino"
        )
        self.femaleRadioButton.grid(row=2, column=2, padx=20, pady=20, sticky="ew")

        self.noneRadioButton = ctk.CTkRadioButton(
            central_frame,
            text="Prefiro não dizer",
            variable=self.genderVar,
            value="Prefere não dizer",
        )
        self.noneRadioButton.grid(row=2, column=3, padx=20, pady=20, sticky="ew")

        # Choice Label
        self.choiceLabel = ctk.CTkLabel(central_frame, text="Turno")
        self.choiceLabel.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # Choice Check boxes
        self.checkboxVar = tk.StringVar(value="Turno")

        self.choice1 = ctk.CTkCheckBox(
            central_frame,
            text="Matutino",
            variable=self.checkboxVar,
            onvalue="Matutino",
            offvalue="c1",
        )
        self.choice1.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        self.choice2 = ctk.CTkCheckBox(
            central_frame,
            text="Vespertino",
            variable=self.checkboxVar,
            onvalue="Vespertino",
            offvalue="c2",
        )
        self.choice2.grid(row=3, column=2, padx=20, pady=20, sticky="ew")

        self.choice3 = ctk.CTkCheckBox(
            central_frame,
            text="Noturno",
            variable=self.checkboxVar,
            onvalue="Noturno (18:01 - 06:00)",
            offvalue="c3",
        )
        self.choice3.grid(row=3, column=3, padx=20, pady=20, sticky="ew")

        # Occupation Label
        self.occupationLabel = ctk.CTkLabel(central_frame, text="Ocupacao")
        self.occupationLabel.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # Occupation combo box
        self.occupationOptionMenu = ctk.CTkOptionMenu(
            central_frame,
            values=[
                "Profissional 1",
                "Profissional 2",
                "Profissional 3",
                "Profissional 4",
            ],
        )
        self.occupationOptionMenu.grid(
            row=4, column=1, padx=20, pady=20, columnspan=2, sticky="ew"
        )

        # Generate Button
        self.generateResultsButton = ctk.CTkButton(
            central_frame, text="Cadastrar", command=self.capture_and_store_data
        )
        self.generateResultsButton.grid(
            row=5, column=1, columnspan=2, padx=20, pady=20, sticky="ew"
        )

        # Text Box
        self.displayBox = ctk.CTkTextbox(central_frame, width=200, height=100)
        self.displayBox.grid(
            row=6, column=0, columnspan=4, padx=20, pady=20, sticky="nsew"
        )

        # Webcam Button
        self.webcam_on = False
        self.webcam_button = ctk.CTkButton(
            central_frame, text="Webcam", command=self.toggle_webcam
        )
        self.webcam_button.grid(row=0, column=5, padx=20, pady=20, sticky="ew")

        # Create a label for displaying the webcam feed
        self.webcam_label = ctk.CTkLabel(central_frame)
        self.webcam_label.grid(row=1, column=5, padx=20, pady=20, sticky="ew")

        self.capture_button = ctk.CTkButton(
            central_frame, text="Capture Image", command=self.capture_images
        )
        self.capture_button.grid(row=2, column=5, padx=20, pady=20, sticky="ew")

    def toggle_webcam(self):
        if not self.webcam_on:
            self.webcam_on = True
            self.webcam_button.configure(text="Stop Webcam")
            self.capture = cv2.VideoCapture(0)

            def update_webcam():
                ret, frame = self.capture.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (120, 120))
                    img = Image.fromarray(frame)
                    img = ImageTk.PhotoImage(image=img)
                    self.webcam_label.configure(image=img)
                    self.webcam_label.image = img
                    self.after(10, update_webcam)

            update_webcam()
        else:
            self.webcam_on = False
            self.webcam_button.configure(text="Start Webcam")
            if hasattr(self, "capture"):
                self.capture.release()
            self.webcam_label.configure(image="")

    def capture_images(self, nameid):
        video = cv2.VideoCapture(0)
        facedetect = cv2.CascadeClassifier("../haarcascade_frontalface_default.xml")
        count = 0

        while count < 100:
            ret, frame = video.read()
            faces = facedetect.detectMultiScale(frame, 1.3, 5)
            for x, y, w, h in faces:
                count += 1
                name = f"./images/{nameid}/{count}.jpg"
                cv2.imwrite(name, frame[y : y + h, x : x + w])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                self.update_progress_label(count)
            cv2.imshow("WindowFrame", frame)
            cv2.waitKey(1)

        video.release()
        cv2.destroyAllWindows()

    def capture_and_store_data(self):
        name = self.nameEntry.get()
        if name:
            nameid = name.lower()
            path = f"images/{nameid}"
            isExist = os.path.exists(path)

            if isExist:
                self.displayBox.delete("0.0", "200.0")
                self.displayBox.insert("0.0", "Nome já registrado")
            else:
                os.makedirs(path)
                self.displayBox.delete("0.0", "200.0")
                self.displayBox.insert("0.0", "Registrando imagens...")

                user_data = {
                    "name": name,
                    "age": self.ageEntry.get(),
                    "gender": self.genderVar.get(),
                    "turno": self.checkboxVar.get(),
                    "occupation": self.occupationOptionMenu.get(),
                }

                self.insert_user_data(user_data)
                self.capture_images(nameid)

                # Agora, após a captura das imagens, você pode salvar as imagens no MongoDB
                for count in range(1, 501):  # 500 imagens
                    img_name = f"./images/{nameid}/{count}.jpg"
                    with open(img_name, "rb") as image_file:
                        img_data = io.BytesIO(image_file.read())
                        self.insert_image(nameid, img_data)
                        self.displayBox.delete("0.0", "200.0")
                        self.displayBox.insert("0.0", f"Imagem {count} registrada")

    def insert_user_data(self, data):
        user_collection = self.mongo_db["users"]
        user_collection.insert_one(data)

    def insert_image(self, nameid, image_data):
        image_collection = self.mongo_db[nameid]
        image_collection.insert_one({"image": image_data.getvalue()})

    def update_progress_label(self, current_count):
        self.progressLabel.configure(text=f"Progress: {current_count}/20")
        self.update_idletasks()


if __name__ == "__main__":
    app = App()
    app.mainloop()
