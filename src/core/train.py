import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import cv2
import os
import numpy as np
import customtkinter as ctk
import threading
import time
import math
import random
from utils.paths import get_model_path, STUDENT_PHOTOS_DIR, ensure_directories_exist

# Check OpenCV version and face recognition module
opencv_version = cv2.__version__
print(f"OpenCV version: {opencv_version}")

face_recognizer_available = False
try:
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer_available = True
    print("Face module loaded successfully")
    print(f"Face recognizer type: {type(face_recognizer)}")
except AttributeError as e:
    print(f"AttributeError: {str(e)}")
    print("Error: cv2.face.LBPHFaceRecognizer_create() is not available")
    print("Make sure you have opencv-contrib-python installed correctly")
except Exception as e:
    print(f"An unexpected error occurred while loading the face module: {str(e)}")

print(f"OpenCV path: {cv2.__file__}")
print(f"Face recognizer available: {face_recognizer_available}")

class Particle:
    def __init__(self, x, y, canvas):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.color = random.choice(["#4CAF50", "#2196F3", "#FFC107", "#E91E63"])
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.canvas = canvas
        self.id = self.canvas.create_oval(x, y, x + self.size, y + self.size, fill=self.color, outline="")

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.canvas.move(self.id, math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed)

    def reset(self, x, y):
        self.canvas.delete(self.id)
        self.x = x
        self.y = y
        self.id = self.canvas.create_oval(x, y, x + self.size, y + self.size, fill=self.color, outline="")

class ParticleSystem:
    def __init__(self, canvas, num_particles):
        self.canvas = canvas
        self.particles = [Particle(random.randint(0, 300), random.randint(0, 300), canvas) for _ in range(num_particles)]

    def update(self):
        for particle in self.particles:
            particle.move()
            if not (0 <= particle.x <= 300 and 0 <= particle.y <= 300):
                particle.reset(random.randint(0, 300), random.randint(0, 300))

    def create_face_shape(self):
        face_outline = [
            (150, 50), (100, 100), (75, 150), (75, 200), (100, 250),
            (150, 300), (200, 250), (225, 200), (225, 150), (200, 100)
        ]
        eyes = [(125, 150), (175, 150)]
        mouth = [(140, 225), (160, 225)]

        for particle in self.particles:
            closest_point = min(face_outline + eyes + mouth, key=lambda p: (p[0] - particle.x) ** 2 + (p[1] - particle.y) ** 2)
            particle.angle = math.atan2(closest_point[1] - particle.y, closest_point[0] - particle.x)

class Train:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.title("Train Data Sets")
        self.root.configure(bg="#1e1e1e")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.setup_gui()

    def setup_gui(self):
        self.setup_background()
        self.create_main_frame()
        self.setup_title()
        self.setup_train_button()
        self.setup_loading_animation()

    def setup_background(self):
        bg_image = self.create_pattern_image()
        self.photoimg_bg = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, 
                                        size=(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        bg_label = ctk.CTkLabel(self.root, image=self.photoimg_bg, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_pattern_image(self):
        width, height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        image = Image.new('RGB', (width, height), color='#1e1e1e')
        draw = ImageDraw.Draw(image)
        
        for x in range(0, width, 30):
            for y in range(0, height, 30):
                draw.rectangle([x, y, x+20, y+20], fill='#2c2c2c', outline='#3a3a3a')
        
        return image.filter(ImageFilter.GaussianBlur(radius=3))

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#2c2c2c", 
                                       border_width=2, border_color="#3a3a3a")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.8)

    def setup_title(self):
        title_label = ctk.CTkLabel(self.root, text="Train Data Sets", 
                                   font=("Roboto", 36, "bold"), text_color="#ffffff")
        title_label.place(relx=0.5, y=30, anchor=tk.CENTER)

    def setup_train_button(self):
        self.train_btn = ctk.CTkButton(self.main_frame, text="TRAIN DATA", command=self.train_classifier,
                                       font=("Roboto", 20, "bold"), fg_color="#4CAF50", hover_color="#45a049")
        self.train_btn.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.3, relheight=0.1)

    def setup_loading_animation(self):
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.progress_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        self.progress_canvas = tk.Canvas(self.progress_frame, width=400, height=200, bg="#2c2c2c", highlightthickness=0)
        self.progress_canvas.pack()

        self.progress_label = ctk.CTkLabel(self.main_frame, text="0%", font=("Roboto", 24, "bold"), text_color="#4CAF50")
        self.progress_label.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=("Roboto", 14))
        self.status_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        self.create_neural_network()

    def animate_loading(self):
        phrases = ["Analyzing faces", "Processing data", "Training model", "Optimizing classifier"]
        phrase_index = 0

        while self.is_training:
            phrase_index = (phrase_index + 1) % len(phrases)
            self.animate_neural_network()
            self.status_label.configure(text=f"{phrases[phrase_index]}...")
            self.root.update()
            time.sleep(0.5)

        self.progress_canvas.delete("all")
        self.progress_label.configure(text="")
        self.status_label.configure(text="")
        self.create_neural_network()

    def train_classifier(self):
        self.train_btn.configure(state="disabled")
        self.is_training = True
        threading.Thread(target=self.animate_loading, daemon=True).start()
        threading.Thread(target=self._train_classifier, daemon=True).start()

    def _train_classifier(self):
        if not face_recognizer_available:
            self.show_error("Face recognition module is not available. Cannot train classifier.")
            return

        try:
            # Ensure the data directory exists
            ensure_directories_exist()
            
            # Use STUDENT_PHOTOS_DIR instead of hardcoded "DATA"
            path = [os.path.join(STUDENT_PHOTOS_DIR, file) for file in os.listdir(STUDENT_PHOTOS_DIR) if file.endswith('.jpg')]

            faces = []
            ids = []

            total_images = len(path)
            if total_images < 2:
                self.show_error("Insufficient training data. You need at least two images to train the model.")
                return

            for index, image in enumerate(path):
                img = Image.open(image).convert('L')
                imageNp = np.array(img, 'uint8')
                id = int(os.path.split(image)[1].split('.')[1])

                faces.append(imageNp)
                ids.append(id)

                # Update progress
                progress = int((index + 1) / total_images * 100)
                self.root.after(0, lambda p=progress: self.update_progress(p))

            self.root.after(0, lambda: self.update_progress(100))
            self.root.after(0, lambda: self.status_label.configure(text="Training classifier..."))

            ids = np.array(ids)

            if len(set(ids)) < 2:
                self.show_error("Insufficient unique individuals. You need images from at least two different people.")
                return

            clf = cv2.face.LBPHFaceRecognizer_create()
            clf.train(faces, ids)
            clf.write(get_model_path("classifier.xml"))

            self.show_success(f"Training datasets completed successfully! {len(faces)} images processed.")
        except Exception as e:
            self.show_error(f"An error occurred during training: {str(e)}")

        self.is_training = False
        self.root.after(0, lambda: self.train_btn.configure(state="normal"))

    def update_progress(self, progress):
        self.progress_label.configure(text=f"{progress}%")

    def show_error(self, message):
        self.is_training = False
        messagebox.showerror("Error", message, parent=self.root)

    def show_success(self, message):
        messagebox.showinfo("Success", message, parent=self.root)

    def create_neural_network(self):
        self.nodes = []
        self.connections = []
        layers = [4, 6, 6, 4]
        y_spacing = 180 / (max(layers) - 1)
        for i, layer_size in enumerate(layers):
            x = 50 + i * 100
            for j in range(layer_size):
                y = 20 + j * y_spacing
                node = self.progress_canvas.create_oval(x-5, y-5, x+5, y+5, fill="#4CAF50", outline="")
                self.nodes.append(node)
                if i > 0:
                    for prev_node in range(sum(layers[:i-1]), sum(layers[:i])):
                        connection = self.progress_canvas.create_line(
                            50 + (i-1) * 100, 20 + (prev_node - sum(layers[:i-1])) * y_spacing,
                            x, y, fill="#2196F3", width=1
                        )
                        self.connections.append(connection)

    def animate_neural_network(self):
        for connection in self.connections:
            if random.random() < 0.1:
                self.progress_canvas.itemconfig(connection, fill="#FFC107", width=2)
            else:
                self.progress_canvas.itemconfig(connection, fill="#2196F3", width=1)
        
        for node in self.nodes:
            if random.random() < 0.1:
                self.progress_canvas.itemconfig(node, fill="#E91E63")
            else:
                self.progress_canvas.itemconfig(node, fill="#4CAF50")

if __name__ == "__main__":
    root = tk.Tk()
    obj = Train(root)
    root.mainloop()
