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
        self.webcam_on = False

    def setup_ui(self):
        central_frame = ctk.CTkFrame(self)
        central_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Progress Label
        self.progressLabel = ctk.CTkLabel(central_frame, text="Progress: 0/20")
        self.progressLabel.grid(
            row=7, column=0, columnspan=4, padx=20, pady=20, sticky="ew"
        )

        # MongoDB Connection
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_client["user_data"]

        labels = ["Nome", "Idade", "Genero", "Turno", "Ocupacao"]
        entries = ["nameEntry", "ageEntry"]

        for label_text, entry_name in zip(labels, entries):
            label = ctk.CTkLabel(central_frame, text=label_text)
            label.grid(
                row=labels.index(label_text), column=0, padx=20, pady=20, sticky="ew"
            )
            entry = ctk.CTkEntry(
                central_frame, placeholder_text=f"{label_text.lower()}..."
            )
            entry.grid(
                row=labels.index(label_text),
                column=1,
                columnspan=3,
                padx=20,
                pady=20,
                sticky="ew",
            )
            setattr(self, entry_name, entry)

        genders = ["Masculino", "Feminino", "Prefere não dizer"]
        self.genderVar = tk.StringVar(value=genders[-1])

        for gender_text in genders:
            gender_rb = ctk.CTkRadioButton(
                central_frame,
                text=gender_text,
                variable=self.genderVar,
                value=gender_text,
            )
            gender_rb.grid(
                row=genders.index(gender_text) + 2,
                column=1,
                padx=20,
                pady=20,
                sticky="ew",
            )

        self.checkboxVar = tk.StringVar(value="Turno")

        shifts = ["Matutino", "Vespertino", "Noturno (18:01 - 06:00)"]

        for shift_text in shifts:
            shift_cb = ctk.CTkCheckBox(
                central_frame,
                text=shift_text,
                variable=self.checkboxVar,
                onvalue=shift_text,
                offvalue="c" + str(shifts.index(shift_text) + 1),
            )
            shift_cb.grid(
                row=shifts.index(shift_text) + 3,
                column=1,
                padx=20,
                pady=20,
                sticky="ew",
            )

        occupations = [
            "Profissional 1",
            "Profissional 2",
            "Profissional 3",
            "Profissional 4",
        ]
        self.occupationOptionMenu = ctk.CTkOptionMenu(central_frame, values=occupations)
        self.occupationOptionMenu.grid(
            row=6, column=1, padx=20, pady=20, columnspan=2, sticky="ew"
        )

        self.generateResultsButton = ctk.CTkButton(
            central_frame, text="Cadastrar", command=self.capture_and_store_data
        )
        self.generateResultsButton.grid(
            row=7, column=0, columnspan=4, padx=20, pady=20, sticky="ew"
        )

        self.displayBox = ctk.CTkTextbox(central_frame, width=200, height=100)
        self.displayBox.grid(
            row=8, column=0, columnspan=4, padx=20, pady=20, sticky="nsew"
        )

        self.webcam_button = ctk.CTkButton(
            central_frame, text="Webcam", command=self.toggle_webcam
        )
        self.webcam_button.grid(row=0, column=4, padx=20, pady=20, sticky="ew")

        self.webcam_label = ctk.CTkLabel(central_frame)
        self.webcam_label.grid(row=1, column=4, padx=20, pady=20, sticky="ew")

        self.capture_button = ctk.CTkButton(
            central_frame, text="Capture Image", command=self.capture_images
        )
        self.capture_button.grid(row=2, column=4, padx=20, pady=20, sticky="ew")

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

    def capture_images(self):
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

                self.capture_images_for_user(nameid)

    def capture_images_for_user(self, nameid):
        video = cv2.VideoCapture(0)
        facedetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        count = 0

        while count < 20:
            ret, frame = video.read()
            faces = facedetect.detectMultiScale(frame, 1.3, 5)
            for x, y, w, h in faces:
                count += 1
                img_name = f"./images/{nameid}/{count}.jpg"
                cv2.imwrite(img_name, frame[y : y + h, x : x + w])
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
                self.capture_images_for_user(nameid)

                for count in range(1, 21):  # 20 imagens
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
