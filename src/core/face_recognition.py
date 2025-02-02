import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import mysql.connector
from datetime import datetime, timedelta
import cv2
import os
import csv
import threading
import time
import logging
import customtkinter as ctk
import numpy as np
from ..utils.paths import get_model_path, get_image_path, get_data_file_path
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME", "face_recognizer")
}

class FaceRecognizer:
    """A class for face detection and recognition."""
    
    def __init__(self):
        """Initialize the face recognizer with required models."""
        self.face_cascade = cv2.CascadeClassifier(get_model_path("haarcascade_frontalface_default.xml"))
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_trained = False
        
    def detect_faces(self, image):
        """Detect faces in the given image.
        
        Args:
            image: numpy array of the image
            
        Returns:
            List of tuples (x, y, w, h) for each detected face
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
        return faces
        
    def train(self, train_dir):
        """Train the face recognition model.
        
        Args:
            train_dir: Directory containing training images organized by person
        """
        faces = []
        labels = []
        label_map = {}
        current_label = 0
        
        for person_dir in os.listdir(train_dir):
            person_path = os.path.join(train_dir, person_dir)
            if not os.path.isdir(person_path):
                continue
                
            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                    
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                detected_faces = self.detect_faces(img)
                
                for (x, y, w, h) in detected_faces:
                    faces.append(gray[y:y+h, x:x+w])
                    labels.append(current_label)
                    
            label_map[current_label] = person_dir
            current_label += 1
            
        if faces:
            self.recognizer.train(faces, np.array(labels))
            self.model_trained = True
            
    def recognize(self, image):
        """Recognize faces in the given image.
        
        Args:
            image: numpy array of the image
            
        Returns:
            List of tuples (label, confidence) for each recognized face
        """
        if not self.is_model_trained():
            return None
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detect_faces(image)
        results = []
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            label, confidence = self.recognizer.predict(face_roi)
            results.append((label, confidence))
            
        return results
        
    def is_model_trained(self):
        """Check if the model has been trained.
        
        Returns:
            bool: True if model is trained, False otherwise
        """
        return self.model_trained

class Face_Recognition1:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.title("Face Recognition Attendance System")
        self.root.configure(bg="#1e1e1e")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.is_running = False
        self.camera_thread = None
        self.current_frame = None
        self.recognition_threshold = 55

        self.face_cascade = cv2.CascadeClassifier(get_model_path("haarcascade_frontalface_default.xml"))
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(get_model_path("classifier.xml"))

        self.db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CONFIG)
        self.stop_event = threading.Event()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_gui()

    def setup_gui(self):
        # Main title
        title_label = ctk.CTkLabel(self.root, text="Face Recognition Attendance System", 
                                 font=("Roboto", 36, "bold"), text_color="#ffffff")
        title_label.place(relx=0.5, y=30, anchor=tk.CENTER)

        # Main container frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#2c2c2c")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.85)

        # Camera feed frame (left side)
        self.camera_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#252525")
        self.camera_frame.place(relx=0.01, rely=0.02, relwidth=0.68, relheight=0.96)
        
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="")
        self.camera_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Info panel frame (right side)
        self.info_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#252525")
        self.info_frame.place(relx=0.71, rely=0.02, relwidth=0.28, relheight=0.96)

        # Recognition Info title
        self.info_label = ctk.CTkLabel(self.info_frame, text="Recognition Info", 
                                     font=("Roboto", 24, "bold"), text_color="#4CAF50")
        self.info_label.place(relx=0.5, rely=0.05, anchor=tk.N)

        # Student info labels
        info_y_positions = {
            'id': 0.2,
            'roll': 0.3,
            'name': 0.4,
            'department': 0.5,
            'semester': 0.6,
            'confidence': 0.7
        }

        for key, pos in info_y_positions.items():
            label = ctk.CTkLabel(self.info_frame, text=f"{key.title()}:", 
                               font=("Roboto", 16), text_color="#ffffff")
            label.place(relx=0.1, rely=pos, anchor=tk.W)
            setattr(self, f"{key}_label", label)

        # Stop Recognition button
        self.toggle_button = ctk.CTkButton(self.info_frame, text="Stop Recognition",
                                         command=self.toggle_face_recog,
                                         font=("Roboto", 20, "bold"),
                                         fg_color="#4CAF50",
                                         hover_color="#45a049",
                                         corner_radius=10)
        self.toggle_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER, relwidth=0.9, relheight=0.1)

        self.setup_image_frames()  # Set up frames for images
        self.setup_buttons()  # Set up buttons

    def setup_image_frames(self):
        # Create a frame for displaying student information
        self.student_info_frame = ctk.CTkFrame(self.info_frame, corner_radius=10, fg_color="#303030")
        self.student_info_frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.5)

        # Create labels for student information
        self.id_label = self.create_info_label(self.student_info_frame, "ID:", 0.05)
        self.roll_label = self.create_info_label(self.student_info_frame, "Roll:", 0.2)
        self.name_label = self.create_info_label(self.student_info_frame, "Name:", 0.35)
        self.department_label = self.create_info_label(self.student_info_frame, "Department:", 0.5)
        self.semester_label = self.create_info_label(self.student_info_frame, "Semester:", 0.65)
        self.confidence_label = self.create_info_label(self.student_info_frame, "Confidence:", 0.80)

        self.attendance_label = ctk.CTkLabel(self.info_frame, text="", font=("Roboto", 18, "bold"))
        self.attendance_label.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

    def create_info_label(self, parent, text, rely):
        # Helper function to create labels for student information
        label = ctk.CTkLabel(parent, text=text, font=("Roboto", 16, "bold"), anchor="w")
        label.place(relx=0.05, rely=rely, relwidth=0.9, relheight=0.1)
        return label

    def setup_buttons(self):
        # Create the main toggle button for starting/stopping face recognition
        self.toggle_button = ctk.CTkButton(self.info_frame, text="Start Recognition", command=self.toggle_face_recog,
                                           font=("Roboto", 20, "bold"), fg_color="#4CAF50", hover_color="#45a049",
                                           corner_radius=10)
        self.toggle_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER, relwidth=0.9, relheight=0.1)

        # Add a pulsing effect to draw attention to the button
        self.pulse_animation(self.toggle_button)

    def pulse_animation(self, widget):
        # Create a pulsing animation effect for the given widget
        current_color = widget.cget("fg_color")
        new_color = self.lighten_color(current_color) if current_color == "#4CAF50" else "#4CAF50"
        widget.configure(fg_color=new_color)
        self.root.after(1000, lambda: self.pulse_animation(widget))

    def lighten_color(self, color):
        # Helper function to lighten a color
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        lighter_rgb = tuple(min(int(c * 1.2), 255) for c in rgb)
        return f"#{lighter_rgb[0]:02x}{lighter_rgb[1]:02x}{lighter_rgb[2]:02x}"

    def toggle_face_recog(self):
        if not self.is_running:
            self.start_face_recog()
            self.toggle_button.configure(text="Stop Recognition", fg_color="#FF5252", hover_color="#FF1744")
        else:
            self.stop_face_recog()
            self.toggle_button.configure(text="Start Recognition", fg_color="#4CAF50", hover_color="#45a049")

    def start_face_recog(self):
        # Start the face recognition process
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            self.toggle_button.configure(text="Stop Recognition", fg_color="#FF5252", hover_color="#FF1744")
            self.camera_thread = threading.Thread(target=self.camera_capture, daemon=True)
            self.camera_thread.start()

    def stop_face_recog(self):
        # Stop the face recognition process
        self.is_running = False
        self.stop_event.set()
        if self.camera_thread:
            self.camera_thread.join(timeout=2)  # Wait for up to 2 seconds
            if self.camera_thread.is_alive():
                logging.warning("Camera thread did not terminate gracefully")
        self.toggle_button.configure(text="Start Recognition", fg_color="#4CAF50", hover_color="#45a049")
        self.clear_camera_output()
        self.clear_info_labels()

    def clear_camera_output(self):
        # Clear the camera output display
        blank_image = Image.new('RGB', (self.camera_frame.winfo_width(), self.camera_frame.winfo_height()), color='#252525')
        blank_imgtk = ctk.CTkImage(light_image=blank_image, dark_image=blank_image, 
                                   size=(self.camera_frame.winfo_width(), self.camera_frame.winfo_height()))
        self.camera_label.configure(image=blank_imgtk)
        self.camera_label.image = blank_imgtk

    def clear_info_labels(self):
        # Reset all info labels
        self.id_label.configure(text="ID:")
        self.roll_label.configure(text="Roll:")
        self.name_label.configure(text="Name:")
        self.department_label.configure(text="Department:")
        self.semester_label.configure(text="Semester:")
        self.confidence_label.configure(text="Confidence:")

    def camera_capture(self):
        video_cap = cv2.VideoCapture(0)
        if not video_cap.isOpened():
            messagebox.showerror("Error", "Failed to open webcam")
            self.stop_face_recog()
            return

        def process_frame_thread():
            while self.is_running and not self.stop_event.is_set():
                ret, frame = video_cap.read()
                if not ret:
                    logging.error("Failed to capture frame")
                    break
                self.current_frame = cv2.flip(frame, 1)
                self.process_frame(self.current_frame)
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage

        processing_thread = threading.Thread(target=process_frame_thread, daemon=True)
        processing_thread.start()

        while self.is_running and not self.stop_event.is_set():
            if self.current_frame is not None:
                self.update_camera_feed()
            time.sleep(0.03)  # Adjust this value to control the update frequency

        video_cap.release()
        processing_thread.join(timeout=1)

    def process_frame(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                # Improved face detection filtering
                if w < 50 or h < 50:  # Skip very small faces
                    continue
                
                # Extract and preprocess face region
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.equalizeHist(face_roi)  # Enhance contrast
                face_roi = cv2.resize(face_roi, (220, 220))
                
                # Perform recognition with confidence check
                id, confidence = self.recognizer.predict(face_roi)
                confidence = 100 - confidence  # Convert confidence to percentage
                
                if confidence > 45:  # Increased threshold for better accuracy
                    self.handle_recognized_face(frame, id, x, y, w, h, confidence)
                else:
                    self.handle_unknown_face(frame, x, y, confidence)

        except Exception as e:
            logging.error(f"Error in process_frame: {str(e)}")

    def update_camera_feed(self):
        # Update the camera feed display
        if self.current_frame is not None:
            cv2image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, 
                                 size=(self.camera_frame.winfo_width(), self.camera_frame.winfo_height()))
            self.camera_label.configure(image=imgtk)
            self.camera_label.image = imgtk

    def handle_recognized_face(self, img, id, x, y, w, h, confidence):
        conn = self.db_pool.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT Name, Roll, Dep, Student_id, Semester FROM student WHERE Student_id=%s", (str(id),))
            result = cursor.fetchone()

            if result:
                n, r, d, i, s = result
                # Draw rectangle with thicker border for better visibility
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                self.display_recognition_info(img, x, y, w, h, i, r, n, d, s, confidence)
                attendance_status = self.mark_attendance(i, r, n, d)
                self.update_attendance_label(attendance_status)
                logging.info(f"Recognized: ID {i}, Name: {n}, Confidence: {confidence}")
            else:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
                cv2.putText(img, "Not Registered", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                self.update_attendance_label("not_registered")
                logging.warning(f"Recognized face (ID: {id}) not found in database. Confidence: {confidence}")
        finally:
            cursor.close()
            conn.close()

    def display_recognition_info(self, img, x, y, w, h, i, r, n, d, s, confidence):
        try:
            # Update info panel labels
            self.id_label.configure(text=f"ID: {i}")
            self.roll_label.configure(text=f"Roll: {r}")
            self.name_label.configure(text=f"Name: {n}")
            self.department_label.configure(text=f"Department: {d}")
            self.semester_label.configure(text=f"Semester: {s}")
            self.confidence_label.configure(text=f"Confidence: {confidence:.2f}%")

            # Draw rectangle and name with shadow for better visibility
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
            
            # Add text background for better readability
            text_size = cv2.getTextSize(n, cv2.FONT_HERSHEY_COMPLEX, 0.8, 2)[0]
            cv2.rectangle(img, (x, y-30), (x + text_size[0], y), (0, 255, 0), -1)
            cv2.putText(img, n, (x, y-10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 2)
            
        except Exception as e:
            logging.error(f"Error in display_recognition_info: {str(e)}")

    def mark_attendance(self, i, r, n, d):
        # Mark attendance for the recognized student
        try:
            now = datetime.now()
            d1 = now.strftime("%d/%m/%Y")
            dtString = now.strftime("%H:%M:%S")
            
            attendance_file = get_data_file_path("attendance.csv")
            
            # Create the file with headers if it doesn't exist
            if not os.path.exists(attendance_file):
                with open(attendance_file, "w", newline="\n") as f:
                    f.write("ID,Roll,Name,Department,Time,Date,Attendance\n")
            
            with open(attendance_file, "r+", newline="\n") as f:
                my_data_list = f.readlines()
                name_list = set()
                last_attendance = {}
                for line in my_data_list:
                    entry = line.strip().split(",")
                    if len(entry) >= 6:
                        name_list.add(entry[0])
                        if entry[0] == i:
                            last_attendance[entry[0]] = datetime.strptime(f"{entry[5]} {entry[4]}", "%d/%m/%Y %H:%M:%S")
                
                if i in last_attendance:
                    if now - last_attendance[i] < timedelta(hours=1):
                        logging.debug(f"Attendance for {n} (ID: {i}) already marked within the last hour.")
                        return False
                
                f.write(f"{i},{r},{n},{d},{dtString},{d1},Present\n")
                logging.debug(f"Attendance marked for {n} (ID: {i})")
                return True
        except Exception as e:
            logging.error(f"Error in mark_attendance: {e}")
            return False

    def update_attendance_label(self, status):
        # Update the attendance status label
        if status == True:
            self.attendance_label.configure(text="Attendance Marked", text_color="#4CAF50")
        elif status == False:
            self.attendance_label.configure(text="Attendance Already Marked", text_color="#FFC107")
        else:
            self.attendance_label.configure(text="Not Registered", text_color="#FF5722")
        
        self.attendance_label.after(3000, self.reset_attendance_label)

    def reset_attendance_label(self):
        # Reset the attendance label after a delay
        self.attendance_label.configure(text="")

    def on_closing(self):
        # Handle window closing event
        self.stop_face_recog()
        self.root.destroy()
        # Check if this is the main window or a child window
        if self.root.master is None:
            self.root.quit()

    def handle_unknown_face(self, frame, x, y, confidence):
        cv2.putText(frame, "Unknown", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        logging.info(f"Unknown face detected. Confidence: {confidence}")
        self.clear_info_labels()
        self.confidence_label.configure(text=f"Confidence: {confidence:.2f}%")

if __name__ == "__main__":
    root = tk.Tk()
    obj = Face_Recognition1(root)
    root.mainloop()
