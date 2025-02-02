import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import mysql.connector
import bcrypt
from tkinter import messagebox
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "face_recognizer")
}

# MySQL Connection
try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255)
    )
    """)
    connection.commit()
except mysql.connector.Error as err:
    print(f"Error: {err}")
    messagebox.showerror("Database Error", f"Unable to connect to the database: {err}")
    exit(1)

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login / Sign Up")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.configure(fg_color="#f6f5f7")
        self.is_logged_in = False

        # Calculate container size based on screen size
        container_width = min(self.winfo_screenwidth(), int(self.winfo_screenwidth() * 0.8))
        container_height = min(self.winfo_screenheight(), int(self.winfo_screenheight() * 0.8))

        self.container = ctk.CTkFrame(self, fg_color="#fff", corner_radius=10, width=container_width, height=container_height)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        frame_width = container_width // 2
        frame_height = container_height

        self.sign_in_frame = ctk.CTkFrame(self.container, fg_color="#fff", width=frame_width, height=frame_height)
        self.sign_in_frame.place(x=0, y=0)

        self.sign_up_frame = ctk.CTkFrame(self.container, fg_color="#fff", width=frame_width, height=frame_height)
        self.sign_up_frame.place(x=frame_width, y=0)

        self.overlay_frame = ctk.CTkFrame(self.container, fg_color="#FF416C", width=frame_width, height=frame_height)
        self.overlay_frame.place(x=frame_width, y=0)

        self.create_sign_in_widgets()
        self.create_sign_up_widgets()
        self.create_overlay_widgets()

    def create_sign_in_widgets(self):
        ctk.CTkLabel(self.sign_in_frame, text="Sign In", font=("Montserrat", 24, "bold")).place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        
        self.sign_in_email = ctk.CTkEntry(self.sign_in_frame, width=250, placeholder_text="Email")
        self.sign_in_email.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        self.sign_in_password = ctk.CTkEntry(self.sign_in_frame, width=250, placeholder_text="Password", show="*")
        self.sign_in_password.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ctk.CTkButton(self.sign_in_frame, text="Sign In", command=self.sign_in, fg_color="#FF4B2B", hover_color="#FF416C").place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    def create_sign_up_widgets(self):
        ctk.CTkLabel(self.sign_up_frame, text="Create Account", font=("Montserrat", 24, "bold")).place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        
        self.sign_up_name = ctk.CTkEntry(self.sign_up_frame, width=250, placeholder_text="Name")
        self.sign_up_name.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
        self.sign_up_email = ctk.CTkEntry(self.sign_up_frame, width=250, placeholder_text="Email")
        self.sign_up_email.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        
        self.sign_up_password = ctk.CTkEntry(self.sign_up_frame, width=250, placeholder_text="Password", show="*")
        self.sign_up_password.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        
        ctk.CTkButton(self.sign_up_frame, text="Sign Up", command=self.sign_up, fg_color="#FF4B2B", hover_color="#FF416C").place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    def create_overlay_widgets(self):
        self.overlay_left = ctk.CTkFrame(self.overlay_frame, fg_color="#FF416C", width=384, height=480)
        self.overlay_left.place(x=0, y=0)
        
        self.overlay_right = ctk.CTkFrame(self.overlay_frame, fg_color="#FF416C", width=384, height=480)
        self.overlay_right.place(x=0, y=0)
        
        ctk.CTkLabel(self.overlay_left, text="Welcome Back!", font=("Montserrat", 24, "bold"), text_color="#fff").place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        ctk.CTkLabel(self.overlay_left, text="To keep connected with us please\nlogin with your personal info", font=("Montserrat", 12), text_color="#fff").place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        ctk.CTkButton(self.overlay_left, text="Sign In", command=self.show_sign_in, fg_color="transparent", border_color="#fff", border_width=2, hover_color="#FF4B2B").place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        ctk.CTkLabel(self.overlay_right, text="Hello, Friend!", font=("Montserrat", 24, "bold"), text_color="#fff").place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        ctk.CTkLabel(self.overlay_right, text="Enter your personal details\nand start journey with us", font=("Montserrat", 12), text_color="#fff").place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        ctk.CTkButton(self.overlay_right, text="Sign Up", command=self.show_sign_up, fg_color="transparent", border_color="#fff", border_width=2, hover_color="#FF4B2B").place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def show_sign_in(self):
        self.overlay_frame.place(x=384, y=0)

    def show_sign_up(self):
        self.overlay_frame.place(x=0, y=0)

    def sign_in(self):
        email = self.sign_in_email.get()
        password = self.sign_in_password.get()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            print("Login successful!")
            self.is_logged_in = True
            self.destroy()  # Close the login window
        else:
            print("Invalid email or password")
            messagebox.showerror("Login Failed", "Invalid email or password")

    def sign_up(self):
        name = self.sign_up_name.get()
        email = self.sign_up_email.get()
        password = self.sign_up_password.get()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            connection.commit()
            print("Registration successful!")
        except mysql.connector.IntegrityError:
            print("Email already exists")

def login_process():
    app = LoginApp()
    app.mainloop()
    return app.is_logged_in

if __name__ == "__main__":
    login_process()