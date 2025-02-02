# Import necessary libraries and modules
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import os
import customtkinter as ctk
import time
import logging
from gui.student import Student
from core.train import Train
from core.face_recognition import Face_Recognition1
from gui.attendance import Attendance
from gui.help_chatbot import HelpChatbot
import cv2
import mysql.connector
from utils.paths import get_image_path, STUDENT_PHOTOS_DIR

# Set up logging to track any errors or important information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Main class for the Face Recognition Attendance System
class Face_Recognition:
    def __init__(self, root):
        self.root = root  # Store the main window object
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")  # Set window size to full screen
        self.root.title("Face Recognition Attendance System")  # Set the window title
        self.root.configure(bg="#1e1e1e")  # Set the background color to dark gray

        # Set the appearance mode and color theme for the custom tkinter widgets
        ctk.set_appearance_mode("dark")  # Set dark mode for the application
        ctk.set_default_color_theme("blue")  # Set blue as the primary color theme

        # Dictionary to store child windows
        self.child_windows = {}  # Initialize an empty dictionary to keep track of open windows

        # Set up the main components of the GUI
        self.setup_background()  # Create and set up the background image
        self.setup_title()  # Create and set up the main title
        self.setup_buttons()  # Create and set up the main menu buttons
        self.setup_help_chatbot()  # Set up the help chatbot button

    def setup_background(self):
        try:
            # Load and process the background image
            bg_image = Image.open(get_image_path("Watercolor03.jpg"))
            bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            bg_image = bg_image.filter(ImageFilter.GaussianBlur(radius=5))
            self.photoimg_bg = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, 
                                            size=(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

            # Create a label with the background image
            bg_label = ctk.CTkLabel(self.root, image=self.photoimg_bg, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Create a semi-transparent overlay on top of the background
            overlay = ctk.CTkCanvas(self.root, bg="#1e1e1e", highlightthickness=0)  # Create a canvas for the overlay
            overlay.place(x=0, y=0, relwidth=1, relheight=1)  # Place the overlay to cover the entire window
            overlay.create_rectangle(0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight(), fill="#1e1e1e", outline="", stipple="gray50")  # Create a semi-transparent rectangle
        except Exception as e:
            # Show an error message if there's a problem setting up the background
            self.show_error("Error setting up background", e)  # Display an error message if background setup fails

    def setup_title(self):
        # Create and place the main title of the application
        self.title_label = ctk.CTkLabel(self.root, text="Face Recognition Attendance System", 
                                        font=("Roboto", 42, "bold"), text_color="#ffffff")  # Create the main title label
        self.title_label.place(relx=0.5, y=50, anchor=tk.CENTER)  # Place the title at the top center of the window
        # Start the title animation
        self.animate_title()  # Begin the title color animation

    def setup_buttons(self):
        # Create a frame to hold all the main menu buttons
        button_frame = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#1e1e1e", border_width=2, border_color="#2c2c2c")
        button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.96, relheight=0.76)

        # Configure the grid layout for the button frame
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        button_frame.grid_rowconfigure((0, 1), weight=1)

        # Define the data for each button (text, image path, and associated function)
        button_data = [
            ("Student Details", get_image_path("profile-removebg.png"), self.student_details),
            ("Face Detect", get_image_path("face.png"), self.Face_Detect_data),
            ("Attendance", get_image_path("istockphoto-1198430065-612x612.jpg"), self.attendance_data),
            ("Train Data", get_image_path("4468206-200.png"), self.train_data),
            ("Photos", get_image_path("photo.png"), self.open_img),
            ("Exit", get_image_path("logout.png"), self.iExit)
        ]

        # Create buttons for each menu item
        for i, (text, img_path, command) in enumerate(button_data):
            row = i // 3
            col = i % 3
            self.create_animated_button(button_frame, text, img_path, command, row, col)

    def create_animated_button(self, parent, text, img_path, command, row, col):
        # Create an animated button with an icon and text
        try:
            # Load and resize the button icon
            img = Image.open(img_path)
            img = img.resize((190, 190), Image.LANCZOS)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(190, 190))

            # Create the button with custom styling
            button = ctk.CTkButton(parent, text=text, image=photo, compound=tk.TOP, command=command,
                                   font=("Roboto", 18, "bold"),
                                   corner_radius=15, fg_color="#2c2c2c", 
                                   hover_color="#3a3a3a", text_color="#ffffff",
                                   width=200, height=180)
            button.grid(row=row, column=col, padx=25, pady=25, sticky="nsew")

            # Bind hover events for button animation
            button.bind("<Enter>", lambda e: self.on_enter(e, button))
            button.bind("<Leave>", lambda e: self.on_leave(e, button))
        except Exception as e:
            # Show an error message if there's a problem creating the button
            self.show_error(f"Error creating button {text}", e)

    def on_enter(self, e, button):
        # Change button appearance when the mouse enters
        button.configure(fg_color="#3a3a3a")
        button.configure(border_color="#ffffff", border_width=2)

    def on_leave(self, e, button):
        # Restore button appearance when the mouse leaves
        button.configure(fg_color="#2c2c2c")
        button.configure(border_color=button.cget("fg_color"), border_width=0)

    def animate_title(self):
        # Animate the main title by changing its color
        colors = ["#ffffff", "#4da6ff"]
        def animate():
            current_color = self.title_label.cget("text_color")
            next_color = colors[(colors.index(current_color) + 1) % len(colors)]
            self.title_label.configure(text_color=next_color)
            self.root.after(2000, animate)
        animate()

    def open_img(self):
        # Open the folder containing student photos
        os.startfile(STUDENT_PHOTOS_DIR)

    def iExit(self):
        # Handle the exit button click
        self.iExit = messagebox.askyesno("Face Recognition", "Are you sure you want to exit?", parent=self.root)
        if self.iExit:
            self.root.quit()

    def create_child_window(self, window_class, *args):
        # Create or focus on an existing child window
        if window_class.__name__ not in self.child_windows or not self.child_windows[window_class.__name__].winfo_exists():
            # Create a new window if it doesn't exist
            new_window = ctk.CTkToplevel(self.root)
            new_window.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            new_window.title(window_class.__name__)
            new_window.attributes('-topmost', True)
            new_window.focus_force()
            self.child_windows[window_class.__name__] = new_window
            return window_class(new_window, *args)
        else:
            # Bring existing window to front
            self.child_windows[window_class.__name__].lift()
            self.child_windows[window_class.__name__].focus_force()
            return None

    def student_details(self):
        # Open the Student Details window
        self.create_child_window(Student)

    def train_data(self):
        # Open the Train Data window
        self.create_child_window(Train)

    def Face_Detect_data(self):
        # Open the Face Detection window
        self.create_child_window(Face_Recognition1)

    def attendance_data(self):
        # Open the Attendance window
        self.create_child_window(Attendance)

    def setup_help_chatbot(self):
        # Set up the help chatbot button
        icon_size = 40
        help_icon = self.create_help_icon(icon_size)

        self.help_button = ctk.CTkButton(self.root, image=help_icon, text="", width=icon_size, height=icon_size,
                                command=self.toggle_help_chatbot, fg_color="transparent",
                                hover_color="#3a3a3a")
        self.help_button.place(relx=0.98, rely=0.98, anchor=tk.SE)

        self.help_chatbot = None
        self.help_window = None
        self.pulse_animation(self.help_button)

    def create_help_icon(self, size):
        # Create a custom help icon
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([0, 0, size, size], fill='#4CAF50')
        font_size = int(size * 0.6)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        text = "?"
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
        position = ((size - text_width) / 2, (size - text_height) / 2)
        draw.text(position, text, font=font, fill='white')
        return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))

    def toggle_help_chatbot(self):
        if self.help_window is None or not self.help_window.winfo_exists():
            self.show_help_chatbot()
        else:
            self.close_help_chatbot()

    def show_help_chatbot(self):
        self.help_window = ctk.CTkToplevel(self.root)
        self.help_window.title("Help Chatbot")
        self.help_window.geometry("900x700+{}+{}".format(
            self.root.winfo_x() + 50,
            self.root.winfo_y() + 50
        ))
        self.help_window.resizable(True, True)
        self.help_window.attributes('-topmost', True)
        
        self.help_chatbot = HelpChatbot(self.help_window, self)
        self.help_chatbot.show_chatbot(self.help_window)

        self.help_window.protocol("WM_DELETE_WINDOW", self.close_help_chatbot)

    def close_help_chatbot(self):
        if self.help_window:
            self.help_window.destroy()
            self.help_window = None
            self.help_chatbot = None

    def pulse_animation(self, button):
        # Create a pulsing animation for the help button
        current_color = button.cget("fg_color")
        new_color = "#3a3a3a" if current_color == "transparent" else "transparent"
        button.configure(fg_color=new_color)
        self.root.after(1000, lambda: self.pulse_animation(button))

    def show_error(self, message, exception):
        # Display an error message and log the error
        logging.error(f"{message}: {str(exception)}")
        messagebox.showerror("Error", f"{message}: {str(exception)}", parent=self.root)

# Main entry point of the application
if __name__ == "__main__":
    root = ctk.CTk()
    obj = Face_Recognition(root)
    root.mainloop()
