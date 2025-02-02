from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
import cv2
import os
import numpy as np
from main import Face_Recognition
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import customtkinter as ctk
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

def main():
    win=Tk()
    app=Login(win)
    win.mainloop()

class DatabaseManager:
    def __init__(self):
        self.db = None
        self.cursor = None
        self.initialize_variables()
        self.connect_to_database()
        self.create_table()

    def initialize_variables(self):
        self.var_f_name = StringVar()
        self.var_l_name = StringVar()
        self.var_phno = StringVar()
        self.var_email = StringVar()
        self.var_sq = StringVar()
        self.var_sqAnn = StringVar()
        self.var_new_pswd = StringVar()
        self.var_confirm_new_pswd = StringVar()

    def connect_to_database(self):
        try:
            self.db = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Unable to connect to the database: {err}")
            exit(1)

    def create_table(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS register (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `First name` VARCHAR(255),
                `Last name` VARCHAR(255),
                `Phone number` VARCHAR(20),
                Email VARCHAR(255) UNIQUE,
                SecurityQ VARCHAR(255),
                SecurityA VARCHAR(255),
                Password VARCHAR(255)
            )
            """)
            self.db.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Unable to create table: {err}")

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()

class Login(DatabaseManager):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.title("Face Recognition Attendance System - Login")
        self.root.configure(bg="#1e1e1e")

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Background image
        self.bg_image = Image.open(r"Image\Training Data Section.png")
        self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
        self.bg_image = self.bg_image.filter(ImageFilter.GaussianBlur(radius=5))
        self.photoimg = ImageTk.PhotoImage(self.bg_image)

        fr_lbl = Label(self.root, image=self.photoimg)
        fr_lbl.place(x=0, y=0, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())

        # Create a semi-transparent overlay
        overlay = Canvas(self.root, bg="#1e1e1e", highlightthickness=0)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.create_rectangle(0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight(), fill="#1e1e1e", outline="", stipple="gray50")

        # Title label
        self.title_label = ctk.CTkLabel(self.root, text="Face Recognition Attendance System", 
                                        font=("Roboto", 42, "bold"), text_color="#ffffff")
        self.title_label.place(relx=0.5, y=50, anchor=tk.CENTER)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#2c2c2c", border_width=2, border_color="#3a3a3a")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.8, relheight=0.7)

        # Create frames for different sections
        self.login_frame = self.create_frame()
        self.register_frame = self.create_frame()
        self.forgot_password_frame = self.create_frame()

        # Initialize variables for registration
        self.var_f_name = tk.StringVar()
        self.var_l_name = tk.StringVar()
        self.var_phno = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_new_pswd = tk.StringVar()
        self.var_confirm_new_pswd = tk.StringVar()
        self.var_sq = tk.StringVar()
        self.var_sqAnn = tk.StringVar()
        self.var_check = tk.IntVar()

        self.create_login_widgets()
        self.create_register_widgets()
        self.create_forgot_password_widgets()

        self.show_login()

    def create_frame(self):
        return ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#252525")

    def create_login_widgets(self):
        login_label = ctk.CTkLabel(self.login_frame, text="Welcome Back!", font=("Roboto", 32, "bold"), text_color="#ffffff")
        login_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Add iU logo
        self.iu_logo = ctk.CTkImage(Image.open(r"Image\iU logo.png"), size=(100, 100))
        ctk.CTkLabel(self.login_frame, image=self.iu_logo, text="").place(relx=0.5, rely=0.25, anchor=tk.CENTER)

        email_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent", width=300, height=50)
        email_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.email_entry = ctk.CTkEntry(email_frame, width=300, height=50, placeholder_text="Email", 
                                        font=("Montserrat", 14), border_color="#4e54c8", fg_color="#2b2b2b", 
                                        text_color="#ffffff", placeholder_text_color="#a0a0a0")
        self.email_entry.place(x=0, y=0)

        password_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent", width=300, height=50)
        password_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

        self.pswd_entry = ctk.CTkEntry(password_frame, width=270, height=50, placeholder_text="Password", 
                                       font=("Montserrat", 14), show="•", border_color="#4e54c8", fg_color="#2b2b2b", 
                                       text_color="#ffffff", placeholder_text_color="#a0a0a0")
        self.pswd_entry.place(x=0, y=0)

        self.button_mode = True
        self.Oeye_btn = ctk.CTkImage(Image.open(r"Image\opene.png"), size=(20, 20))
        self.b2 = ctk.CTkButton(password_frame, image=self.Oeye_btn, text="", width=30, height=30, 
                                command=self.hide, fg_color="transparent", hover_color="#3a3a3a")
        self.b2.place(x=270, y=10)

        login_btn = ctk.CTkButton(self.login_frame, text="Sign In", command=self.login, width=300, height=50, 
                                  font=("Roboto", 16, "bold"), fg_color="#4e54c8", hover_color="#3f45a0", corner_radius=25)
        login_btn.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        forgot_btn = ctk.CTkButton(self.login_frame, text="Forgot Password?", command=self.show_forgot_password, 
                                   width=200, font=("Roboto", 12), fg_color="transparent", text_color="#4e54c8", hover_color="#3a3a3a")
        forgot_btn.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        adduser_btn = ctk.CTkButton(self.login_frame, text="Add New User", command=self.show_register, 
                                    width=200, font=("Roboto", 12), fg_color="transparent", text_color="#4e54c8", hover_color="#3a3a3a")
        adduser_btn.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    def create_register_widgets(self):
        register_label = ctk.CTkLabel(self.register_frame, text="Create New Account", font=("Montserrat", 32, "bold"), text_color="#ffffff")
        register_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

        # Create a scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(self.register_frame, width=350, height=400, fg_color="transparent")
        scrollable_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

        fields = [
            ("First Name", self.var_f_name),
            ("Last Name", self.var_l_name),
            ("Phone Number", self.var_phno),
            ("Email", self.var_email),
            ("New Password", self.var_new_pswd),
            ("Confirm Password", self.var_confirm_new_pswd)
        ]

        for i, (text, variable) in enumerate(fields):
            label = ctk.CTkLabel(scrollable_frame, text=text, font=("Montserrat", 14), text_color="#ffffff")
            label.pack(pady=(10, 0), anchor="w")
            entry = ctk.CTkEntry(scrollable_frame, textvariable=variable, width=300, height=40, 
                                 placeholder_text=text, font=("Montserrat", 12), border_color="#4e54c8", 
                                 fg_color="#2b2b2b", text_color="#ffffff", placeholder_text_color="#a0a0a0")
            entry.pack(pady=(0, 10))

            if text == "New Password" or text == "Confirm Password":
                entry.configure(show="•")

        security_questions = ["Select", "What is your favorite food?", "Who is your best friend?", "What is your favorite car?", "What is your favorite movie?", "What is your favorite TV show?", "Who is your favorite teacher?"]
        
        sq_label = ctk.CTkLabel(scrollable_frame, text="Security Question", font=("Montserrat", 14), text_color="#ffffff")
        sq_label.pack(pady=(10, 0), anchor="w")
        self.sq_combo = ctk.CTkOptionMenu(scrollable_frame, variable=self.var_sq, values=security_questions,
                                          font=("Montserrat", 12), width=300, fg_color="#2b2b2b", text_color="#ffffff",
                                          button_color="#4e54c8", button_hover_color="#3f45a0", dropdown_fg_color="#2b2b2b", dropdown_text_color="#ffffff")
        self.sq_combo.pack(pady=(0, 10))

        sa_label = ctk.CTkLabel(scrollable_frame, text="Security Answer", font=("Montserrat", 14), text_color="#ffffff")
        sa_label.pack(pady=(10, 0), anchor="w")
        self.sqAnn = ctk.CTkEntry(scrollable_frame, textvariable=self.var_sqAnn, width=300, height=40, 
                                  placeholder_text="Security Answer", font=("Montserrat", 12), border_color="#4e54c8", 
                                  fg_color="#2b2b2b", text_color="#ffffff", placeholder_text_color="#a0a0a0")
        self.sqAnn.pack(pady=(0, 10))

        self.var_check = tk.IntVar()
        terms_check = ctk.CTkCheckBox(scrollable_frame, text="I agree to the Terms and Conditions", variable=self.var_check,
                                      font=("Montserrat", 12), text_color="#ffffff", fg_color="#4e54c8", hover_color="#3f45a0", checkmark_color="#ffffff")
        terms_check.pack(pady=10)

        register_btn = ctk.CTkButton(scrollable_frame, text="Register", command=self.register_data, width=300, height=50, 
                                     font=("Montserrat", 16, "bold"), fg_color="#4e54c8", hover_color="#3f45a0", corner_radius=25)
        register_btn.pack(pady=20)

        back_btn = ctk.CTkButton(self.register_frame, text="Back to Login", command=self.show_login, 
                                 width=200, font=("Montserrat", 12), fg_color="transparent", text_color="#ffffff", hover_color="#3a3a3a")
        back_btn.place(relx=0.1, rely=0.05, anchor=tk.NW)

    def create_forgot_password_widgets(self):
        forgot_label = ctk.CTkLabel(self.forgot_password_frame, text="Forgot Password", font=("Roboto", 32, "bold"), text_color="#ffffff")
        forgot_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        self.forgot_email = ctk.CTkEntry(self.forgot_password_frame, width=300, height=50, placeholder_text="Email", 
                                         font=("Roboto", 14), fg_color="#2b2b2b", text_color="#ffffff", placeholder_text_color="#a0a0a0")
        self.forgot_email.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        security_questions = ["Select", "What is your favorite food?", "Who is your best friend?", "What is your favorite car?", 
                              "What is your favorite movie?", "What is your favorite TV show?", "Who is your favorite teacher?"]
        self.sq_combo_forgot = ctk.CTkOptionMenu(self.forgot_password_frame, values=security_questions,
                                                 font=("Roboto", 12), width=300, fg_color="#2b2b2b", text_color="#ffffff",
                                                 button_color="#4e54c8", button_hover_color="#3f45a0", 
                                                 dropdown_fg_color="#2b2b2b", dropdown_text_color="#ffffff")
        self.sq_combo_forgot.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        self.sqAnn_forgot = ctk.CTkEntry(self.forgot_password_frame, width=300, height=50, placeholder_text="Security Answer", 
                                         font=("Roboto", 14), fg_color="#2b2b2b", text_color="#ffffff", placeholder_text_color="#a0a0a0")
        self.sqAnn_forgot.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        self.new_password = ctk.CTkEntry(self.forgot_password_frame, width=300, height=50, placeholder_text="New Password", 
                                         font=("Roboto", 14), show="•", fg_color="#2b2b2b", text_color="#ffffff", placeholder_text_color="#a0a0a0")
        self.new_password.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

        reset_btn = ctk.CTkButton(self.forgot_password_frame, text="Reset Password", command=self.reset_password, width=300, height=50, 
                                  font=("Roboto", 16, "bold"), fg_color="#4e54c8", hover_color="#3f45a0", corner_radius=25)
        reset_btn.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        back_btn = ctk.CTkButton(self.forgot_password_frame, text="Back to Login", command=self.show_login, 
                                 width=200, font=("Roboto", 12), fg_color="transparent", text_color="#4e54c8", hover_color="#3a3a3a")
        back_btn.place(relx=0.1, rely=0.05, anchor=tk.NW)

    def show_login(self):
        self.register_frame.place_forget()
        self.forgot_password_frame.place_forget()
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.9)

    def show_register(self):
        self.login_frame.place_forget()
        self.forgot_password_frame.place_forget()
        self.register_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.9)

    def show_forgot_password(self):
        self.login_frame.place_forget()
        self.register_frame.place_forget()
        self.forgot_password_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.9, relheight=0.9)

    def hide(self):
        if self.button_mode:
            close_img = ctk.CTkImage(Image.open(r"Image\closee.png"), size=(20, 20))
            self.b2.configure(image=close_img)
            self.pswd_entry.configure(show="")
            self.button_mode = False
        else:
            open_img = ctk.CTkImage(Image.open(r"Image\opene.png"), size=(20, 20))
            self.b2.configure(image=open_img)
            self.pswd_entry.configure(show="•")
            self.button_mode = True

    def login(self):
        if self.email_entry.get() == "" or self.pswd_entry.get() == "":
            messagebox.showerror("Error", "All fields are required!", parent=self.root)
        else:
            try:
                self.cursor.execute("SELECT * FROM register WHERE Email=%s", (self.email_entry.get(),))
                row = self.cursor.fetchone()
                if row is None:
                    messagebox.showerror("Error!", "Invalid Email or Password")
                else:
                    # Implement proper password hashing and verification here
                    if self.pswd_entry.get() == row[7]:  # Assuming password is at index 7
                        messagebox.showinfo("Success", "Login Successful!")
                        self.show_main_window()
                    else:
                        messagebox.showerror("Error!", "Invalid Email or Password")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"An error occurred: {err}")

    def reset_password(self):
        email = self.forgot_email.get()
        security_question = self.sq_combo_forgot.get()
        security_answer = self.sqAnn_forgot.get()
        new_password = self.new_password.get()

        if email == "" or security_question == "Select" or security_answer == "" or new_password == "":
            messagebox.showerror("Error", "All fields are required!", parent=self.root)
        else:
            try:
                query = "SELECT * FROM register WHERE Email=%s AND SecurityQ=%s AND SecurityA=%s"
                value = (email, security_question, security_answer)
                self.cursor.execute(query, value)
                row = self.cursor.fetchone()

                if row is None:
                    messagebox.showerror("Error", "Invalid email or security answer!", parent=self.root)
                else:
                    update_query = "UPDATE register SET Password=%s WHERE Email=%s"
                    update_value = (new_password, email)
                    self.cursor.execute(update_query, update_value)
                    self.db.commit()
                    messagebox.showinfo("Success", "Password reset successfully!", parent=self.root)
                    self.show_login()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database Error: {err}", parent=self.root)

    def forgot_password_window(self):
        self.show_forgot_password()

    def register_data(self):
        if self.var_f_name.get() == "" or self.var_email.get() == "" or self.var_sq.get() == "Select" or self.var_phno.get() == "" or self.var_l_name.get() == "":
            messagebox.showerror("Field Error", "All fields are required!")
        elif self.var_new_pswd.get() != self.var_confirm_new_pswd.get():
            messagebox.showerror("Mismatch Error", "Password does not match!")
        elif self.var_check.get() == 0:
            messagebox.showerror("T&C Error", "Please agree terms & condition")
        else:
            try:
                self.cursor.execute(
                    "INSERT INTO register (`First name`, `Last name`, `Phone number`, Email, SecurityQ, SecurityA, Password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        self.var_f_name.get(),
                        self.var_l_name.get(),
                        self.var_phno.get(),
                        self.var_email.get(),
                        self.var_sq.get(),
                        self.var_sqAnn.get(),
                        self.var_new_pswd.get(),
                    )
                )
                self.db.commit()
                messagebox.showinfo("Success", "Registration Successful")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"An error occurred: {err}")

    def return_login(self):
        self.root.destroy()

    def show_main_window(self):
        self.new_window = Toplevel(self.root)
        self.app = Face_Recognition(self.new_window)

if __name__ == "__main__":
    main()
