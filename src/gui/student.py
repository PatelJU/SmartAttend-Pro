from tkinter import Tk
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter
import customtkinter as ctk
import mysql.connector
import cv2
import os
import time
import re
from tkinter import messagebox
from tkinter import END
from contextlib import contextmanager
import logging
import csv
from tkinter import filedialog
from tkcalendar import DateEntry
from datetime import date
from utils.paths import get_log_file_path, get_image_path, get_model_path, STUDENT_PHOTOS_DIR, ensure_directories_exist
import win32gui
import win32con
import win32process
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "username": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "face_recognizer")
}

mydata = []  # Temporary storage for data operations

# Configure logging
logging.basicConfig(
    filename=get_log_file_path(),
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MovableImagePreview:
    """A draggable and resizable image preview window."""
    def __init__(self, parent, image_path, size=(300, 300)):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.overrideredirect(True)
        self.top.attributes('-topmost', True)
        self.top.attributes('-alpha', 0.0)  # Start fully transparent
        
        self.original_image = Image.open(image_path)
        self.size = size
        self.min_size = (100, 100)
        self.max_size = (800, 800)
        self.aspect_ratio = self.original_image.width / self.original_image.height
        self.resize_image()
        
        self.canvas = tk.Canvas(self.top, width=self.size[0]+40, height=self.size[1]+40, highlightthickness=0, bg='#2c2c2c')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        
        self.draw_elements()
        
        self.canvas.bind('<ButtonPress-1>', self.start_move)
        self.canvas.bind('<B1-Motion>', self.move)
        self.canvas.bind('<ButtonPress-3>', self.start_resize)
        self.canvas.bind('<B3-Motion>', self.resize)
        self.canvas.bind('<ButtonRelease-3>', self.stop_resize)
        
        self.x = 0
        self.y = 0
        self.resizing = False
        
        self.fade_in()

    def resize_image(self):
        width, height = self.size
        if width / height > self.aspect_ratio:
            width = int(height * self.aspect_ratio)
        else:
            height = int(width / self.aspect_ratio)
        self.image = self.original_image.copy()
        self.image.thumbnail((width, height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.image)

    def draw_elements(self):
        self.canvas.delete("all")
        
        # Create gradient background
        self.create_gradient_background()
        
        # Create drop shadow
        shadow_color = '#1a1a1a'
        for i in range(5):
            offset = i * 2
            self.canvas.create_rectangle(10+offset, 10+offset, self.size[0]+30-offset, self.size[1]+30-offset, 
                                         fill=shadow_color, outline=shadow_color)
        
        # Create main image with border
        self.border = self.canvas.create_rectangle(15, 15, self.size[0]+25, self.size[1]+25, 
                                                   outline='#4CAF50', width=2)
        
        # Calculate position to center the image
        x_offset = (self.size[0] - self.photo.width()) // 2 + 20
        y_offset = (self.size[1] - self.photo.height()) // 2 + 20
        self.image_on_canvas = self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo)
        
        close_button = tk.Button(self.canvas, text="×", command=self.close, 
                                 bg='#F44336', fg='white', font=('Arial', 16, 'bold'),
                                 bd=0, padx=5, pady=0)
        self.close_button_window = self.canvas.create_window(self.size[0]+30, 10, anchor=tk.NE, window=close_button)
        
        # Add resize handle
        self.resize_handle = self.canvas.create_polygon(self.size[0]+30, self.size[1]+30,
                                                        self.size[0]+30, self.size[1]+40,
                                                        self.size[0]+40, self.size[1]+30,
                                                        fill='#4CAF50', outline='#45a049')
        self.canvas.tag_bind(self.resize_handle, '<Enter>', lambda e: self.canvas.config(cursor='sizing'))
        self.canvas.tag_bind(self.resize_handle, '<Leave>', lambda e: self.canvas.config(cursor=''))

    def create_gradient_background(self):
        gradient_steps = 20
        start_color = (44, 44, 44)  # #2c2c2c
        end_color = (58, 58, 58)    # #3a3a3a
        
        for i in range(gradient_steps):
            r = int(start_color[0] + (end_color[0] - start_color[0]) * i / gradient_steps)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * i / gradient_steps)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * i / gradient_steps)
            color = f'#{r:02x}{g:02x}{b:02x}'
            y0 = i * self.size[1] // gradient_steps
            y1 = (i + 1) * self.size[1] // gradient_steps
            self.canvas.create_rectangle(0, y0, self.size[0]+40, y1, fill=color, outline=color)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.top.winfo_x() + deltax
        y = self.top.winfo_y() + deltay
        self.top.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.x = event.x
        self.y = event.y
        self.resizing = True

    def resize(self, event):
        if self.resizing:
            new_width = max(min(event.x - self.x, self.max_size[0]), self.min_size[0])
            new_height = max(min(event.y - self.y, self.max_size[1]), self.min_size[1])
            self.size = (new_width, new_height)
            self.resize_image()
            self.redraw_elements()
            self.top.geometry(f"{new_width + 40}x{new_height + 40}")

    def stop_resize(self, event):
        self.resizing = False

    def redraw_elements(self):
        self.canvas.delete("all")
        self.canvas.config(width=self.size[0] + 40, height=self.size[1] + 40)
        self.draw_elements()

    def fade_in(self):
        alpha = self.top.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.1
            self.top.attributes('-alpha', alpha)
            self.top.after(20, self.fade_in)

    def close(self):
        self.top.destroy()

class DatabaseConnection:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            username=self.username,
            password=self.password,
            database=self.database
        )
        return self.connection

    def cursor(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection.cursor()

    def commit(self):
        if self.connection:
            self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()

# Initialize the DatabaseConnection
db = DatabaseConnection(**DB_CONFIG)

class Student:
    def __init__(self, root):
        # Initialize the main window and set up the GUI
        self.root = root
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.title("Student Management System")
        self.root.configure(bg="#1e1e1e")

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize variables
        self.initialize_variables()

    def initialize_variables(self):
        # Initialize all variables used in the student management system
        self.var_dep = ctk.StringVar()
        self.var_branch = ctk.StringVar()
        self.var_sem = ctk.StringVar()
        self.var_id = ctk.StringVar()
        self.var_name = ctk.StringVar()
        self.var_div = ctk.StringVar()
        self.var_roll = ctk.StringVar()
        self.var_gender = ctk.StringVar()
        self.var_dob = ctk.StringVar()
        self.var_email = ctk.StringVar()
        self.var_phone = ctk.StringVar()
        self.var_address = ctk.StringVar()
        self.var_com_search = ctk.StringVar()
        self.var_search = ctk.StringVar()
        self.var_radio1 = ctk.StringVar(value="No")

        self.setup_gui()

    def setup_gui(self):
        self.setup_background()
        self.create_main_frame()
        self.setup_left_frame()
        self.setup_right_frame()
        self.setup_student_info_frame()
        self.setup_buttons_frame()
        self.setup_table_frame()
        self.fetch_data()

    def setup_background(self):
        bg_image = Image.open(get_image_path("abstract-black-texture-background-hexagon_206725-413.jpg"))
        bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
        bg_image = bg_image.filter(ImageFilter.GaussianBlur(radius=5))
        self.photoimg_bg = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, 
                                        size=(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

        bg_label = ctk.CTkLabel(self.root, image=self.photoimg_bg, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_overlay()
        self.create_title()

    def create_overlay(self):
        overlay = ctk.CTkCanvas(self.root, bg="#1e1e1e", highlightthickness=0)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.create_rectangle(0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight(), 
                                 fill="#1e1e1e", outline="", stipple="gray50")

    def create_title(self):
        title_label = ctk.CTkLabel(self.root, text="Student Management System", 
                                   font=("Roboto", 36, "bold"), text_color="#ffffff")
        title_label.place(relx=0.5, y=30, anchor=tk.CENTER)

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#2c2c2c", 
                                       border_width=2, border_color="#3a3a3a")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.85)

    def setup_left_frame(self):
        self.Left_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#252525")
        self.Left_frame.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)

        self.create_current_course_frame()

    def create_current_course_frame(self):
        current_course_frame = ctk.CTkFrame(self.Left_frame, corner_radius=10, fg_color="#303030", width=640, height=150)
        current_course_frame.place(x=10, y=10)

        self.create_department_field(current_course_frame)
        self.create_branch_field(current_course_frame)
        self.create_semester_field(current_course_frame)

    def create_department_field(self, parent):
        dep_label = ctk.CTkLabel(parent, text="Department:", font=("Roboto", 12))
        dep_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        dep_combo = ctk.CTkComboBox(parent, variable=self.var_dep, values=("Select Department", "B.tech"),
                                    font=("Roboto", 12), state="readonly", width=200)
        dep_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        dep_combo.set("Select Department")

    def create_branch_field(self, parent):
        branch_label = ctk.CTkLabel(parent, text="Branch:", font=("Roboto", 12))
        branch_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

        branch_combo = ctk.CTkComboBox(parent, variable=self.var_branch, 
                                       values=("Select branch", "CSE", "I.T.", "Mechanical"),
                                       font=("Roboto", 12), state="readonly", width=200)
        branch_combo.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        branch_combo.set("Select branch")

    def create_semester_field(self, parent):
        sem_label = ctk.CTkLabel(parent, text="Semester:", font=("Roboto", 12))
        sem_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        sem_combo = ctk.CTkComboBox(parent, variable=self.var_sem, 
                                    values=("Select Semester", "1", "2", "3", "4", "5", "6", "7", "8"),
                                    font=("Roboto", 12), state="readonly", width=200)
        sem_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        sem_combo.set("Select Semester")

    def setup_student_info_frame(self):
        class_student_frame = ctk.CTkFrame(self.Left_frame, corner_radius=10, fg_color="#303030")
        class_student_frame.place(relx=0.02, rely=0.22, relwidth=0.96, relheight=0.60)

        self.create_student_id_field(class_student_frame)
        self.create_student_name_field(class_student_frame)
        self.create_class_division_field(class_student_frame)
        self.create_roll_no_field(class_student_frame)
        self.create_gender_field(class_student_frame)
        self.create_dob_field(class_student_frame)
        self.create_email_field(class_student_frame)
        self.create_phone_field(class_student_frame)
        self.create_address_field(class_student_frame)
        self.create_photo_sample_radio_buttons(class_student_frame)

    def create_student_id_field(self, parent):
        studentId_label = ctk.CTkLabel(parent, text="Student ID:", font=("Roboto", 12))
        studentId_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        studentID_entry = ctk.CTkEntry(parent, textvariable=self.var_id, font=("Roboto", 12), width=200)
        studentID_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

    def create_student_name_field(self, parent):
        studentName_label = ctk.CTkLabel(parent, text="Student Name:", font=("Roboto", 12))
        studentName_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)

        studentName_entry = ctk.CTkEntry(parent, textvariable=self.var_name, font=("Roboto", 12), width=200)
        studentName_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

    def create_class_division_field(self, parent):
        class_div_label = ctk.CTkLabel(parent, text="Class Division:", font=("Roboto", 12))
        class_div_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        div_combo = ctk.CTkComboBox(parent, variable=self.var_div, 
                                    values=("Select Division", "A", "B", "C", "D", "E", "F"),
                                    font=("Roboto", 12), state="readonly", width=200)
        div_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        div_combo.set("Select Division")

    def create_roll_no_field(self, parent):
        roll_no_label = ctk.CTkLabel(parent, text="Roll No:", font=("Roboto", 12))
        roll_no_label.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)

        roll_no_entry = ctk.CTkEntry(parent, textvariable=self.var_roll, font=("Roboto", 12), width=200)
        roll_no_entry.grid(row=1, column=3, padx=10, pady=5, sticky=tk.W)

    def create_gender_field(self, parent):
        gender_label = ctk.CTkLabel(parent, text="Gender:", font=("Roboto", 12))
        gender_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        gender_combo = ctk.CTkComboBox(parent, variable=self.var_gender,
                                       values=("Select Gender", "Male", "Female", "Other"),
                                       font=("Roboto", 12), state="readonly", width=200)
        gender_combo.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        gender_combo.set("Select Gender")

    def create_dob_field(self, parent):
        dob_label = ctk.CTkLabel(parent, text="DOB:", font=("Roboto", 12))
        dob_label.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)

        # Create a StringVar to store the selected date
        self.var_dob = tk.StringVar()

        # Create a custom style for the DateEntry widget
        style = ttk.Style(parent)
        style.theme_use('clam')
        style.configure('my.DateEntry',
                        fieldbackground='#333333',
                        background='#333333',
                        foreground='white',
                        arrowcolor='white')

        # Create the DateEntry widget
        dob_entry = DateEntry(parent, width=18, background='#333333', foreground='white',
                              borderwidth=2, year=2000, date_pattern='yyyy-mm-dd',
                              style='my.DateEntry', textvariable=self.var_dob)
        dob_entry.grid(row=2, column=3, padx=10, pady=5, sticky=tk.W)

        # Set the maximum date to today (to prevent future dates)
        dob_entry.config(maxdate=date.today())

        # Create a button to open the calendar
        calendar_button = ctk.CTkButton(parent, text="📅", width=30, height=30,
                                        command=lambda: dob_entry.drop_down())
        calendar_button.grid(row=2, column=4, padx=(0, 10), pady=5, sticky=tk.W)

        # Bind the <<DateEntrySelected>> event to update the StringVar
        dob_entry.bind("<<DateEntrySelected>>", lambda e: self.var_dob.set(dob_entry.get()))

    def create_email_field(self, parent):
        email_label = ctk.CTkLabel(parent, text="Email:", font=("Roboto", 12))
        email_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)

        email_entry = ctk.CTkEntry(parent, textvariable=self.var_email, font=("Roboto", 12), width=200)
        email_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

    def create_phone_field(self, parent):
        phone_label = ctk.CTkLabel(parent, text="Phone No:", font=("Roboto", 12))
        phone_label.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)

        phone_entry = ctk.CTkEntry(parent, textvariable=self.var_phone, font=("Roboto", 12), width=200)
        phone_entry.grid(row=3, column=3, padx=10, pady=5, sticky=tk.W)

    def create_address_field(self, parent):
        address_label = ctk.CTkLabel(parent, text="Address:", font=("Roboto", 12))
        address_label.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)

        address_entry = ctk.CTkEntry(parent, textvariable=self.var_address, font=("Roboto", 12), width=200)
        address_entry.grid(row=4, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W+tk.E)

    def create_photo_sample_radio_buttons(self, parent):
        self.var_radio1 = ctk.StringVar(value="No")
        
        radio_frame = ctk.CTkFrame(parent, fg_color="transparent")
        radio_frame.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky=tk.W)

        radiobtn1 = ctk.CTkRadioButton(radio_frame, variable=self.var_radio1, value="Yes", text="Take Photo Sample", font=("Roboto", 12))
        radiobtn1.grid(row=0, column=0, padx=10, pady=5)

        radiobtn2 = ctk.CTkRadioButton(radio_frame, variable=self.var_radio1, value="No", text="No Photo Sample", font=("Roboto", 12))
        radiobtn2.grid(row=0, column=1, padx=10, pady=5)

    def setup_buttons_frame(self):
        # Create Buttons Frame
        btn_frame = ctk.CTkFrame(self.Left_frame, corner_radius=10, fg_color="#303030")
        btn_frame.place(relx=0.02, rely=0.84, relwidth=0.96, relheight=0.14)

        # Photo Sample buttons
        take_photo_btn = ctk.CTkButton(btn_frame, text="Take Photo Sample", command=self.generate_dataset, 
                                       font=("Roboto", 12, "bold"), fg_color="#FF9800", hover_color="#F57C00")
        take_photo_btn.place(relx=0.02, rely=0.05, relwidth=0.96, relheight=0.25)

        # CRUD buttons
        save_btn = ctk.CTkButton(btn_frame, text="Save", command=self.add_data, 
                                 font=("Roboto", 12, "bold"), fg_color="#4CAF50", hover_color="#45a049")
        save_btn.place(relx=0.02, rely=0.35, relwidth=0.23, relheight=0.25)

        update_btn = ctk.CTkButton(btn_frame, text="Update", command=self.update_data, 
                                   font=("Roboto", 12, "bold"), fg_color="#2196F3", hover_color="#1976D2")
        update_btn.place(relx=0.27, rely=0.35, relwidth=0.23, relheight=0.25)

        delete_btn = ctk.CTkButton(btn_frame, text="Delete", command=self.delete_data, 
                                   font=("Roboto", 12, "bold"), fg_color="#F44336", hover_color="#D32F2F")
        delete_btn.place(relx=0.52, rely=0.35, relwidth=0.23, relheight=0.25)

        reset_btn = ctk.CTkButton(btn_frame, text="Reset", command=self.reset_data, 
                                  font=("Roboto", 12, "bold"), fg_color="#9E9E9E", hover_color="#757575")
        reset_btn.place(relx=0.77, rely=0.35, relwidth=0.21, relheight=0.25)

        # Show Current Photo button
        show_photo_btn = ctk.CTkButton(btn_frame, text="Show Current Photo", command=self.show_current_photo, 
                                       font=("Roboto", 12, "bold"), fg_color="#673AB7", hover_color="#512DA8")
        show_photo_btn.place(relx=0.02, rely=0.65, relwidth=0.96, relheight=0.25)

    def setup_right_frame(self):
        self.Right_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#252525")
        self.Right_frame.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)

        self.create_search_system()

    def create_search_system(self):
        Search_frame = ctk.CTkFrame(self.Right_frame, corner_radius=10, fg_color="#303030", width=740, height=80)
        Search_frame.place(x=10, y=10)

        search_label = ctk.CTkLabel(Search_frame, text="Search By:", font=("Roboto", 12))
        search_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        search_combo = ctk.CTkComboBox(Search_frame, variable=self.var_com_search, 
                                       values=("Select", "Roll", "Phone"),
                                       font=("Roboto", 12), state="readonly", width=150)
        search_combo.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)

        search_entry = ctk.CTkEntry(Search_frame, textvariable=self.var_search, font=("Roboto", 12), width=150)
        search_entry.grid(row=0, column=2, padx=5, pady=10, sticky=tk.W)

        search_btn = ctk.CTkButton(Search_frame, text="Search", command=self.search_data, font=("Roboto", 12), width=120)
        search_btn.grid(row=0, column=3, padx=5, pady=10)

        showAll_btn = ctk.CTkButton(Search_frame, text="Show All", command=self.fetch_data, font=("Roboto", 12), width=120)
        showAll_btn.grid(row=0, column=4, padx=5, pady=10)

    def setup_table_frame(self):
        table_frame = ctk.CTkFrame(self.Right_frame, corner_radius=10, fg_color="#303030")
        table_frame.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.83)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2c2c2c", foreground="white", fieldbackground="#2c2c2c")
        style.map('Treeview', background=[('selected', '#22559b')])

        scroll_x = ctk.CTkScrollbar(table_frame, orientation="horizontal")
        scroll_y = ctk.CTkScrollbar(table_frame, orientation="vertical")

        self.student_table = ttk.Treeview(table_frame, column=("dep", "branch", "sem", "id", "name", "div", "roll", "gender", "dob", "email", "phone", "address", "photo"),
                                          xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.configure(command=self.student_table.xview)
        scroll_y.configure(command=self.student_table.yview)

        self.setup_table_columns()

        self.student_table.pack(fill=tk.BOTH, expand=1)
        self.student_table.bind("<ButtonRelease-1>", self.get_cursor)

    def setup_table_columns(self):
        columns = ["dep", "branch", "sem", "id", "name", "div", "roll", "gender", "dob", "email", "phone", "address", "photo"]
        column_names = ["Department", "Branch", "Semester", "StudentId", "Name", "Division", "Roll No", "Gender", "DOB", "Email", "Phone", "Address", "PhotoSampleStatus"]

        for col, name in zip(columns, column_names):
            self.student_table.heading(col, text=name)
            self.student_table.column(col, width=100)

        self.student_table["show"] = "headings"

    #====================== Generate data set tack photo samples ========================
    def generate_dataset(self):
        """
        Generate a dataset of student face images.
        Captures multiple photos of the student's face using the webcam,
        processes them for face detection, and saves them for training.
        """
        if self.var_dep.get() == "Select Department" or self.var_name.get() == "" or self.var_id.get() == "":
            messagebox.showerror("Error", "All Fields are required", parent=self.root)
            return

        try:
            # Save student data first
            self.save_student_data()

            # Ensure directories exist
            ensure_directories_exist()

            # Load face detection model
            face_classifier = cv2.CascadeClassifier(get_model_path("haarcascade_frontalface_default.xml"))

            def face_cropped(img):
                if img is None:
                    return None
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    face_cropped = img[y:y+h, x:x+w]
                    return face_cropped
                return None

            def force_window_top(window_name):
                """Force a window to stay on top using Win32 API"""
                try:
                    hwnd = win32gui.FindWindow(None, window_name)
                    if hwnd:
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                except Exception as e:
                    print(f"Error setting window position: {e}")

            def window_monitor():
                """Monitor and keep windows on top"""
                while self.capture_running:
                    force_window_top("Photo Capture")
                    force_window_top("Cropped Face")
                    time.sleep(0.1)  # Small delay to prevent high CPU usage

            # Create instruction window
            instruction_window = ctk.CTkToplevel(self.root)
            instruction_window.title("Photo Capture Instructions")
            instruction_window.geometry("400x200")
            instruction_window.configure(fg_color="#2c2c2c")
            instruction_window.transient(self.root)
            instruction_window.grab_set()
            instruction_window.focus_force()
            
            # Position instruction window
            x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 200) // 2
            instruction_window.geometry(f"400x200+{x}+{y}")
            
            instructions = ctk.CTkLabel(
                instruction_window,
                text="Instructions:\n\n"
                     "1. Press SPACE to capture a photo\n"
                     "2. Press ESC to stop capturing\n"
                     "3. Press ENTER when finished\n\n"
                     "Target: 100 photos",
                font=("Roboto", 14),
                justify="left"
            )
            instructions.pack(pady=20)
            
            progress_label = ctk.CTkLabel(
                instruction_window,
                text="Progress: 0/100 photos captured",
                font=("Roboto", 12)
            )
            progress_label.pack(pady=10)

            # Variables for capture control
            self.capture_running = True
            self.img_counter = 0

            def update_progress():
                if instruction_window.winfo_exists():
                    progress_label.configure(text=f"Progress: {self.img_counter}/100 photos captured")
                    instruction_window.update()

            def stop_capture():
                self.capture_running = False
                instruction_window.destroy()

            instruction_window.protocol("WM_DELETE_WINDOW", stop_capture)

            def capture_photos():
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    messagebox.showerror("Error", "Could not open camera", parent=self.root)
                    return

                try:
                    # Create named windows
                    cv2.namedWindow("Photo Capture", cv2.WINDOW_NORMAL)
                    cv2.namedWindow("Cropped Face", cv2.WINDOW_NORMAL)
                    
                    # Position the windows
                    cv2.moveWindow("Photo Capture", 400, 100)
                    cv2.moveWindow("Cropped Face", 900, 100)

                    # Start window monitor thread
                    monitor_thread = threading.Thread(target=window_monitor, daemon=True)
                    monitor_thread.start()

                    while self.capture_running and self.img_counter < 100:
                        ret, frame = cap.read()
                        if not ret:
                            break

                        # Show the frame
                        cv2.imshow("Photo Capture", frame)
                        
                        key = cv2.waitKey(1)
                        if key == 27:  # ESC
                            if messagebox.askyesno("Confirm", "Are you sure you want to stop capturing?", 
                                                 parent=instruction_window):
                                break
                        elif key == 32:  # SPACE
                            face = face_cropped(frame)
                            if face is not None:
                                self.img_counter += 1
                                face = cv2.resize(face, (450, 450))
                                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                                file_path = os.path.join(STUDENT_PHOTOS_DIR, 
                                                       f"user.{self.var_id.get()}.{self.img_counter}.jpg")
                                cv2.imwrite(file_path, face)
                                
                                # Show progress
                                cv2.putText(face, f"Images Captured: {self.img_counter}/100", 
                                          (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2)
                                cv2.imshow("Cropped Face", face)
                                
                                # Update progress in main thread
                                self.root.after(0, update_progress)
                        
                        elif key == 13:  # ENTER
                            if self.img_counter > 0:
                                break

                finally:
                    self.capture_running = False
                    cap.release()
                    cv2.destroyAllWindows()
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.finish_capture(instruction_window))

            # Start capture in a separate thread
            capture_thread = threading.Thread(target=capture_photos, daemon=True)
            capture_thread.start()

        except Exception as es:
            messagebox.showerror("Error", f"Error capturing photos: {str(es)}", parent=self.root)
            self.capture_running = False

    def finish_capture(self, instruction_window):
        """Handle cleanup and final steps after capture is complete"""
        try:
            if instruction_window.winfo_exists():
                instruction_window.destroy()
            
            if self.img_counter > 0:
                messagebox.showinfo("Success", 
                                  f"Dataset generation completed! {self.img_counter} images captured.", 
                                  parent=self.root)
                self.update_photo_sample_status()
                self.fetch_data()
            else:
                messagebox.showwarning("Warning", "No images were captured.", parent=self.root)
        except:
            pass  # Window might already be destroyed

    def save_student_data(self):
        if not self.validate_data():
            return

        try:
            with db.cursor() as cursor:
                # Check if student already exists
                cursor.execute("SELECT * FROM student WHERE Student_id=%s", (self.var_id.get(),))
                existing_student = cursor.fetchone()

                if existing_student:
                    # Update existing student
                    cursor.execute("""UPDATE student SET 
                        Dep=%s, Branch=%s, Semester=%s, Name=%s, Division=%s, Roll=%s,
                        Gender=%s, Dob=%s, Email=%s, Phone=%s, Address=%s
                        WHERE Student_id=%s""", (
                        self.var_dep.get(), self.var_branch.get(), self.var_sem.get(),
                        self.var_name.get(), self.var_div.get(), self.var_roll.get(),
                        self.var_gender.get(), self.var_dob.get(), self.var_email.get(),
                        self.var_phone.get(), self.var_address.get(), self.var_id.get()
                    ))
                else:
                    # Insert new student
                    cursor.execute("""INSERT INTO student 
                        (Dep, Branch, Semester, Student_id, Name, Division, Roll, Gender, Dob, Email, Phone, Address)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                        self.var_dep.get(), self.var_branch.get(), self.var_sem.get(),
                        self.var_id.get(), self.var_name.get(), self.var_div.get(),
                        self.var_roll.get(), self.var_gender.get(), self.var_dob.get(),
                        self.var_email.get(), self.var_phone.get(), self.var_address.get()
                    ))
            db.commit()
            messagebox.showinfo("Success", "Student data saved successfully", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def update_photo_sample_status(self):
        try:
            with db.cursor() as cursor:
                cursor.execute("UPDATE student SET PhotoSample='Yes' WHERE Student_id=%s", (self.var_id.get(),))
            db.commit()
        except Exception as es:
            messagebox.showerror("Error", f"Failed to update photo sample status: {str(es)}", parent=self.root)

    def show_current_photo(self):
        try:
            student_id = self.var_id.get()
            if not student_id:
                messagebox.showwarning("Warning", "Please select a student first", parent=self.root)
                return

            # Look for the first photo of the student
            photo_pattern = f"user.{student_id}.1.jpg"
            photo_path = os.path.join(STUDENT_PHOTOS_DIR, photo_pattern)

            if not os.path.exists(photo_path):
                messagebox.showinfo("No Photo", "This student has no photos captured yet.", parent=self.root)
                return

            # Create a new window to show the photo
            photo_window = ctk.CTkToplevel(self.root)
            photo_window.title("Student Photo")
            photo_window.geometry("500x600")
            photo_window.configure(fg_color="#2c2c2c")
            photo_window.transient(self.root)
            photo_window.grab_set()

            # Center the window
            x = self.root.winfo_x() + (self.root.winfo_width() - 500) // 2
            y = self.root.winfo_y() + (self.root.winfo_height() - 600) // 2
            photo_window.geometry(f"500x600+{x}+{y}")

            # Load and display the photo
            photo = Image.open(photo_path)
            photo = photo.resize((450, 450), Image.LANCZOS)
            photo_img = ctk.CTkImage(light_image=photo, dark_image=photo, size=(450, 450))
            
            # Create frame for photo
            photo_frame = ctk.CTkFrame(photo_window, fg_color="#1e1e1e", corner_radius=10)
            photo_frame.pack(pady=20, padx=20, fill="both", expand=True)

            # Display student info
            info_text = f"Student ID: {student_id}\nName: {self.var_name.get()}\nDepartment: {self.var_dep.get()}"
            info_label = ctk.CTkLabel(photo_frame, text=info_text, font=("Roboto", 14))
            info_label.pack(pady=10)

            # Display photo
            photo_label = ctk.CTkLabel(photo_frame, image=photo_img, text="")
            photo_label.pack(pady=10)

            # Keep a reference to prevent garbage collection
            photo_label.image = photo_img

            # Close button
            close_btn = ctk.CTkButton(photo_frame, text="Close", 
                                     command=photo_window.destroy,
                                     font=("Roboto", 12))
            close_btn.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Error showing photo: {str(e)}", parent=self.root)

    def search_data(self):
        if self.var_com_search.get() == "Select":
            messagebox.showerror("Error", "Please select search criteria", parent=self.root)
        elif self.var_search.get() == "":
            messagebox.showerror("Error", "Please enter search value", parent=self.root)
        else:
            try:
                conn = self.get_db_connection()
                if conn is None:
                    return

                my_cursor = conn.cursor()

                if self.var_com_search.get() == "Roll":
                    my_cursor.execute("SELECT * FROM student WHERE Roll LIKE %s", ('%' + self.var_search.get() + '%',))
                elif self.var_com_search.get() == "Phone":
                    my_cursor.execute("SELECT * FROM student WHERE Phone LIKE %s", ('%' + self.var_search.get() + '%',))

                data = my_cursor.fetchall()

                if len(data) != 0:
                    self.student_table.delete(*self.student_table.get_children())
                    for i, row in enumerate(data):
                        self.student_table.insert("", tk.END, values=row)
                        if i % 2 == 0:
                            self.student_table.tag_configure(f'evenrow{i}', background='#3a3a3a')
                            self.student_table.item(self.student_table.get_children()[-1], tags=(f'evenrow{i}',))
                else:
                    messagebox.showinfo("Info", "No record found", parent=self.root)
                
                conn.close()
            except Exception as es:
                messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def add_data(self):
        if self.var_dep.get() == "Select Department" or self.var_name.get() == "" or self.var_id.get() == "":
            messagebox.showerror("Error", "All Fields are required", parent=self.root)
        else:
            try:
                self.save_student_data()
                self.fetch_data()
                self.reset_data()
            except Exception as es:
                messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def fetch_data(self):
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM student")
                data = cursor.fetchall()

                if len(data) != 0:
                    self.student_table.delete(*self.student_table.get_children())
                    for i, row in enumerate(data):
                        self.student_table.insert("", tk.END, values=row)
                        if i % 2 == 0:
                            self.student_table.tag_configure(f'evenrow{i}', background='#3a3a3a')
                            self.student_table.item(self.student_table.get_children()[-1], tags=(f'evenrow{i}',))
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def get_cursor(self, event=""):
        cursor_focus = self.student_table.focus()
        content = self.student_table.item(cursor_focus)
        data = content["values"]

        if data:
            self.var_dep.set(data[0])
            self.var_branch.set(data[1])
            self.var_sem.set(data[2])
            self.var_id.set(data[3])
            self.var_name.set(data[4])
            self.var_div.set(data[5])
            self.var_roll.set(data[6])
            self.var_gender.set(data[7])
            self.var_dob.set(data[8])
            self.var_email.set(data[9])
            self.var_phone.set(data[10])
            self.var_address.set(data[11])
            self.var_radio1.set(data[12])

    def update_data(self):
        # Updates existing student data in the database
        if self.var_dep.get() == "Select Department" or self.var_name.get() == "" or self.var_id.get() == "":
            messagebox.showerror("Error", "All Fields are required", parent=self.root)
        elif not self.validate_data():
            return
        else:
            try:
                Update = messagebox.askyesno("Update", "Do you want to update this student's details?", parent=self.root)
                if Update:
                    with db.cursor() as cursor:
                        cursor.execute("UPDATE student SET Dep=%s,Branch=%s,Semester=%s,Name=%s,Division=%s,Roll=%s,Gender=%s,Dob=%s,Email=%s,Phone=%s,Address=%s,PhotoSample=%s WHERE Student_id=%s", (
                            self.var_dep.get(),
                            self.var_branch.get(),
                            self.var_sem.get(),
                            self.var_name.get(),
                            self.var_div.get(),
                            self.var_roll.get(),
                            self.var_gender.get(),
                            self.var_dob.get(),
                            self.var_email.get(),
                            self.var_phone.get(),
                            self.var_address.get(),
                            self.var_radio1.get(),
                            self.var_id.get()
                        ))
                    messagebox.showinfo("Success", "Student details successfully updated", parent=self.root)
                    self.fetch_data()
                    self.reset_data()
            except Exception as es:
                messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def delete_data(self):
        if self.var_id.get() == "":
            messagebox.showerror("Error", "Student ID must be required", parent=self.root)
        else:
            try:
                delete = messagebox.askyesno("Student Delete Page", "Do you want to delete this student and all associated photos?", parent=self.root)
                if delete > 0:
                    with db.cursor() as cursor:
                        # Delete student from database
                        sql = "DELETE FROM student WHERE Student_id=%s"
                        val = (self.var_id.get(),)
                        cursor.execute(sql, val)

                    # Delete associated photos
                    student_id = self.var_id.get()
                    ensure_directories_exist()  # Ensure the directory exists
                    if os.path.exists(STUDENT_PHOTOS_DIR):
                        for filename in os.listdir(STUDENT_PHOTOS_DIR):
                            if filename.startswith(f"user.{student_id}."):
                                file_path = os.path.join(STUDENT_PHOTOS_DIR, filename)
                                try:
                                    os.remove(file_path)
                                except Exception as e:
                                    logging.error(f"Failed to delete photo {file_path}: {str(e)}")

                    self.fetch_data()
                    self.reset_data()
                    messagebox.showinfo("Delete", "Successfully deleted student details and associated photos", parent=self.root)
                else:
                    if not delete:
                        return
            except Exception as es:
                messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

    def reset_data(self):
        # Resets all input fields to their default values
        self.var_dep.set("Select Department")
        self.var_branch.set("Select Branch")
        self.var_sem.set("Select Semester")
        self.var_id.set("")
        self.var_name.set("")
        self.var_div.set("Select Division")
        self.var_roll.set("")
        self.var_gender.set("Male")
        self.var_dob.set("")
        self.var_email.set("")
        self.var_phone.set("")
        self.var_address.set("")
        self.var_radio1.set("")

    def validate_data(self):
        # Validates the input data before saving or updating
        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, self.var_email.get()):
            messagebox.showerror("Error", "Invalid email format", parent=self.root)
            return False

        # Phone number validation (assuming 10-digit format)
        phone_regex = r'^\d{10}$'
        if not re.match(phone_regex, self.var_phone.get()):
            messagebox.showerror("Error", "Invalid phone number format (should be 10 digits)", parent=self.root)
            return False

        # Date of birth validation (assuming format: YYYY-MM-DD)
        dob_regex = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(dob_regex, self.var_dob.get()):
            messagebox.showerror("Error", "Invalid date of birth format (should be YYYY-MM-DD)", parent=self.root)
            return False

        return True

    def get_db_connection(self):
        # Establishes a connection to the database
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to database: {err}", parent=self.root)
            return None

    def export_data(self):
        # Exports student data to a CSV file
        try:
            # Ask user which fields to export
            fields = ['ID', 'Department', 'Branch', 'Semester', 'Name', 'Division', 'Roll', 'Gender', 'DOB', 'Email', 'Phone', 'Address', 'PhotoSample']
            export_fields = []
            for field in fields:
                if messagebox.askyesno("Export", f"Do you want to export {field}?"):
                    export_fields.append(field)

            if not export_fields:
                messagebox.showinfo("Export", "No fields selected for export")
                return

            with db.cursor() as cursor:
                cursor.execute(f"SELECT {','.join(export_fields)} FROM student")
                data = cursor.fetchall()

            if len(data) > 0:
                file_path = filedialog.asksaveasfilename(defaultextension='.csv')
                if file_path:
                    with open(file_path, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(export_fields)
                        writer.writerows(data)
                    messagebox.showinfo("Export Successful", f"Data exported to {file_path}", parent=self.root)
            else:
                messagebox.showinfo("No Data", "No data to export", parent=self.root)
        except Exception as es:
            logging.error(f"Error in export_data: {str(es)}")
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

if __name__ == "__main__":
    root = Tk()
    obj = Student(root)
    root.mainloop()

