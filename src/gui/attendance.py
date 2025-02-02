import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFilter
import customtkinter as ctk
import mysql.connector
import cv2
import os
import csv
from tkinter import filedialog
import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import win32com.client
import pythoncom
import time
import pandas as pd
import math
from utils.paths import get_image_path

class Attendance:
    def __init__(self, root):
        self.root = root  # Initialize the main window
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")  # Set window size to full screen
        self.root.title("Attendance Management System")  # Set the window title
        self.root.configure(bg="#1e1e1e")  # Set the background color to dark grey

        # Set theme for custom tkinter
        ctk.set_appearance_mode("dark")  # Set the appearance mode to dark
        ctk.set_default_color_theme("blue")  # Set the color theme to blue

        # Initialize variables for storing attendance data
        self.var_atten_id = tk.StringVar()  # Variable to store attendance ID
        self.var_atten_roll = tk.StringVar()  # Variable to store roll number
        self.var_atten_name = tk.StringVar()  # Variable to store student name
        self.var_atten_dep = tk.StringVar()  # Variable to store department
        self.var_atten_time = tk.StringVar()  # Variable to store attendance time
        self.var_atten_date = tk.StringVar()  # Variable to store attendance date
        self.var_atten_attendance = tk.StringVar()  # Variable to store attendance status
        
        self.mydata = []  # List to store attendance data
        self.current_file = None  # Variable to store the current file being worked on
        self.excel = None  # Variable to store Excel application instance

        self.setup_gui()  # Call method to set up the graphical user interface

    def setup_gui(self):
        self.setup_background()  # Set up the background of the window
        self.create_main_frame()  # Create the main frame of the window
        self.setup_title()  # Set up the title of the window
        self.setup_left_frame()  # Set up the left frame of the window
        self.setup_right_frame()  # Set up the right frame of the window

    def setup_background(self):
        try:
            bg_image = Image.open(get_image_path("Watercolor03.jpg"))
            bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
            bg_image = bg_image.filter(ImageFilter.GaussianBlur(radius=5))
            self.photoimg_bg = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, 
                                          size=(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            
            bg_label = ctk.CTkLabel(self.root, image=self.photoimg_bg, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Create overlay
            overlay = ctk.CTkCanvas(self.root, bg="#1e1e1e", highlightthickness=0)
            overlay.place(x=0, y=0, relwidth=1, relheight=1)
            overlay.create_rectangle(0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight(), 
                                   fill="#1e1e1e", outline="", stipple="gray50")
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up background: {str(e)}", parent=self.root)

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#2c2c2c", 
                                       border_width=2, border_color="#3a3a3a")  # Create the main frame with custom styling
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.85)  # Place the main frame in the center of the window

    def setup_title(self):
        title_label = ctk.CTkLabel(self.root, text="Attendance Management System", 
                                   font=("Roboto", 36, "bold"), text_color="#ffffff")  # Create the title label
        title_label.place(relx=0.5, y=30, anchor=tk.CENTER)  # Place the title label at the top center of the window

    def setup_left_frame(self):
        self.Left_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#252525")  # Create the left frame
        self.Left_frame.place(relx=0.01, rely=0.02, relwidth=0.48, relheight=0.96)  # Place the left frame within the main frame

        self.create_attendance_details_frame()  # Create the frame for attendance details
        self.create_buttons_frame()  # Create the frame for buttons

    def create_attendance_details_frame(self):
        attendance_details_frame = ctk.CTkFrame(self.Left_frame, corner_radius=10, fg_color="#303030")  # Create a frame for attendance details
        attendance_details_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.7)  # Place the attendance details frame

        # Create entry fields for various attendance details
        self.create_entry_field(attendance_details_frame, "StudentID:", self.var_atten_id, 0, 0)
        self.create_entry_field(attendance_details_frame, "Roll:", self.var_atten_roll, 1, 0)
        self.create_entry_field(attendance_details_frame, "Student Name:", self.var_atten_name, 2, 0)
        self.create_entry_field(attendance_details_frame, "Department:", self.var_atten_dep, 3, 0)
        self.create_entry_field(attendance_details_frame, "Time:", self.var_atten_time, 4, 0)
        self.create_entry_field(attendance_details_frame, "Date:", self.var_atten_date, 5, 0)
        
        # Create a combobox for attendance status
        self.create_combobox(attendance_details_frame, "Attendance Status:", self.var_atten_attendance, 
                             ["Status", "Present", "Absent"], 6, 0)

    def create_entry_field(self, parent, label_text, variable, row, column):
        label = ctk.CTkLabel(parent, text=label_text, font=("Roboto", 14))  # Create a label for the entry field
        label.grid(row=row, column=column, padx=10, pady=5, sticky=tk.W)  # Place the label in the grid

        entry = ctk.CTkEntry(parent, textvariable=variable, font=("Roboto", 14), width=220)  # Create an entry field
        entry.grid(row=row, column=column+1, padx=10, pady=5, sticky=tk.W)  # Place the entry field in the grid

    def create_combobox(self, parent, label_text, variable, values, row, column):
        label = ctk.CTkLabel(parent, text=label_text, font=("Roboto", 14))  # Create a label for the combobox
        label.grid(row=row, column=column, padx=10, pady=5, sticky=tk.W)  # Place the label in the grid

        combobox = ctk.CTkComboBox(parent, variable=variable, values=values,
                                   font=("Roboto", 14), state="readonly", width=220)  # Create a combobox
        combobox.grid(row=row, column=column+1, padx=10, pady=5, sticky=tk.W)  # Place the combobox in the grid
        combobox.set(values[0])  # Set the default value of the combobox

    def create_buttons_frame(self):
        btn_frame = ctk.CTkFrame(self.Left_frame, corner_radius=10, fg_color="#303030")  # Create a frame for buttons
        btn_frame.place(relx=0.02, rely=0.74, relwidth=0.96, relheight=0.24)  # Place the buttons frame

        # Create Import CSV button
        import_btn = ctk.CTkButton(btn_frame, text="Import CSV", command=self.importCsv, 
                                   font=("Roboto", 12, "bold"), fg_color="#4CAF50", hover_color="#45a049")
        import_btn.place(relx=0.02, rely=0.1, relwidth=0.46, relheight=0.35)

        # Create Export CSV button
        export_btn = ctk.CTkButton(btn_frame, text="Export CSV", command=self.exportCsv, 
                                   font=("Roboto", 12, "bold"), fg_color="#2196F3", hover_color="#1976D2")
        export_btn.place(relx=0.52, rely=0.1, relwidth=0.46, relheight=0.35)

        # Create Update button
        update_btn = ctk.CTkButton(btn_frame, text="Update", command=self.update_attendance, 
                                   font=("Roboto", 12, "bold"), fg_color="#FF9800", hover_color="#F57C00")
        update_btn.place(relx=0.02, rely=0.55, relwidth=0.46, relheight=0.35)

        # Create Reset button
        reset_btn = ctk.CTkButton(btn_frame, text="Reset", command=self.reset_data, 
                                  font=("Roboto", 12, "bold"), fg_color="#9E9E9E", hover_color="#757575")
        reset_btn.place(relx=0.52, rely=0.55, relwidth=0.46, relheight=0.35)

    def setup_right_frame(self):
        self.Right_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#252525")  # Create the right frame
        self.Right_frame.place(relx=0.51, rely=0.02, relwidth=0.48, relheight=0.96)  # Place the right frame

        self.setup_table_frame()  # Set up the table frame within the right frame

    def setup_table_frame(self):
        table_frame = ctk.CTkFrame(self.Right_frame, corner_radius=10, fg_color="#303030")  # Create a frame for the table
        table_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)  # Place the table frame

        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)  # Create horizontal scrollbar
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)  # Create vertical scrollbar

        style = ttk.Style()  # Create a style object for the treeview
        style.configure("Treeview.Heading", font=('Roboto', 12, 'bold'))  # Configure the style for treeview headings
        style.configure("Treeview", font=('Roboto', 11), rowheight=25)  # Configure the style for treeview rows

        # Create the treeview for displaying attendance data
        self.AttendanceReportTable = ttk.Treeview(table_frame, column=("id", "roll", "name", "department", "time", "date", "attendance"), 
                                                  xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)  # Pack the horizontal scrollbar
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)  # Pack the vertical scrollbar

        scroll_x.config(command=self.AttendanceReportTable.xview)  # Configure horizontal scrollbar
        scroll_y.config(command=self.AttendanceReportTable.yview)  # Configure vertical scrollbar

        # Configure the headings for each column in the treeview
        self.AttendanceReportTable.heading("id", text="Attendance ID")
        self.AttendanceReportTable.heading("roll", text="Roll")
        self.AttendanceReportTable.heading("name", text="Name")
        self.AttendanceReportTable.heading("department", text="Department")
        self.AttendanceReportTable.heading("time", text="Time")
        self.AttendanceReportTable.heading("date", text="Date")
        self.AttendanceReportTable.heading("attendance", text="Attendance")

        self.AttendanceReportTable["show"] = "headings"  # Show only the headings in the treeview

        # Configure the width for each column in the treeview
        self.AttendanceReportTable.column("id", width=120)
        self.AttendanceReportTable.column("roll", width=100)
        self.AttendanceReportTable.column("name", width=150)
        self.AttendanceReportTable.column("department", width=150)
        self.AttendanceReportTable.column("time", width=100)
        self.AttendanceReportTable.column("date", width=100)
        self.AttendanceReportTable.column("attendance", width=120)

        self.AttendanceReportTable.pack(fill=tk.BOTH, expand=1)  # Pack the treeview to fill the frame

        self.AttendanceReportTable.bind("<ButtonRelease-1>", self.get_cursor)  # Bind the get_cursor method to button release event

    def fetchData(self, rows):
        self.AttendanceReportTable.delete(*self.AttendanceReportTable.get_children())  # Clear existing data in the treeview
        for i in rows:
            if len(i) >= 7:
                # Remove the leading single quote from roll number when displaying in treeview
                display_row = i.copy()
                if display_row[1].startswith("'"):
                    display_row[1] = display_row[1][1:]
                self.AttendanceReportTable.insert("", tk.END, values=display_row)  # Insert each row of data into the treeview

    def importCsv(self):
        self.mydata.clear()
        fln = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open CSV", filetypes=(("CSV File", "*.csv"), ("All File", "*.*")), parent=self.root)
        if fln:
            try:
                with open(fln) as myfile:
                    csvread = csv.reader(myfile, delimiter=",")
                    for i in csvread:
                        if len(i) > 1:
                            i[1] = f"'{i[1]}"
                        self.mydata.append(i)
                self.fetchData(self.mydata)
                self.current_file = fln
                messagebox.showinfo("Success", f"Data imported successfully from {fln}", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Error importing data: {str(e)}", parent=self.root)

    def exportCsv(self):
        try:
            if len(self.mydata) < 1:
                messagebox.showerror("No Data", "No data to export", parent=self.root)  # Show error if no data to export
                return False
            fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save CSV", filetypes=(("CSV File", "*.csv"), ("All File", "*.*")), parent=self.root)  # Open file dialog to save CSV
            with open(fln, mode="w", newline="") as myfile:
                exp_write = csv.writer(myfile, delimiter=",")  # Create a CSV writer object
                for i in self.mydata:
                    exp_write.writerow(i)  # Write each row of data to the CSV file
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)  # Show error message if export fails

    def get_cursor(self, event=""):
        cursor_row = self.AttendanceReportTable.focus()  # Get the focused row in the treeview
        content = self.AttendanceReportTable.item(cursor_row)  # Get the content of the focused row
        rows = content['values']  # Extract the values from the row
        if rows:
            # Set the values of the entry fields based on the selected row
            self.var_atten_id.set(rows[0])
            self.var_atten_roll.set(rows[1])
            self.var_atten_name.set(rows[2])
            self.var_atten_dep.set(rows[3])
            self.var_atten_time.set(rows[4])
            self.var_atten_date.set(rows[5])
            self.var_atten_attendance.set(rows[6])
        else:
            messagebox.showinfo("No Selection", "Please select a row from the table.")  # Show info message if no row is selected

    def reset_data(self):
        # Reset all entry fields to empty strings
        self.var_atten_id.set("")
        self.var_atten_roll.set("")
        self.var_atten_name.set("")
        self.var_atten_dep.set("")
        self.var_atten_time.set("")
        self.var_atten_date.set("")
        self.var_atten_attendance.set("")

    def update_attendance(self):
        if not self.current_file:
            messagebox.showerror("Error", "Please import a CSV file first", parent=self.root)  # Show error if no file is imported
            return

        try:
            # Get the values from the entry fields
            atten_id = self.var_atten_id.get()
            atten_roll = self.var_atten_roll.get()
            atten_name = self.var_atten_name.get()
            atten_dep = self.var_atten_dep.get()
            atten_time = self.var_atten_time.get()
            atten_date = self.var_atten_date.get()
            atten_attendance = self.var_atten_attendance.get()

            if not all([atten_id, atten_roll, atten_name, atten_dep, atten_time, atten_date, atten_attendance]):
                messagebox.showwarning("Incomplete Data", "Please fill all fields", parent=self.root)  # Show warning if any field is empty
                return

            Update = messagebox.askyesno("Update", "Are you sure you want to update this student's attendance?", parent=self.root)  # Confirm update action
            if Update > 0:
                self.show_loading_animation()  # Show loading animation
                self.root.after(100, self.perform_update, atten_id, atten_roll, atten_name, atten_dep, atten_time, atten_date, atten_attendance)  # Perform update after a short delay
        except Exception as es:
            messagebox.showerror("Error", f"Due To: {str(es)}", parent=self.root)  # Show error message if update fails

    def perform_update(self, atten_id, atten_roll, atten_name, atten_dep, atten_time, atten_date, atten_attendance):
        updated = False
        for i, row in enumerate(self.mydata):
            if len(row) >= 7 and str(row[0]) == atten_id:
                self.mydata[i] = [atten_id, atten_roll, atten_name, atten_dep, atten_time, atten_date, atten_attendance]
                updated = True
                break

        if updated:
            # Update CSV file
            self.update_csv_file()

            # Update Excel file
            self.update_excel(self.current_file)

            # Update treeview
            self.fetchData(self.mydata)
            
            # Update the specific item in the treeview
            for item in self.AttendanceReportTable.get_children():
                values = self.AttendanceReportTable.item(item)['values']
                if str(values[0]) == atten_id:
                    self.AttendanceReportTable.item(item, values=[atten_id, atten_roll, atten_name, atten_dep, atten_time, atten_date, atten_attendance])
                    self.AttendanceReportTable.see(item)
                    break

            self.root.after(500, self.show_success_message)
        else:
            self.root.after(500, self.show_not_found_message)

    def update_excel(self, file_path):
        try:
            pythoncom.CoInitialize()  # Initialize COM library
            if not self.excel:
                self.excel = win32com.client.Dispatch("Excel.Application")  # Create Excel application instance
                self.excel.Visible = False  # Make Excel application invisible

            workbook = None
            for wb in self.excel.Workbooks:
                if os.path.abspath(wb.FullName) == os.path.abspath(file_path):
                    workbook = wb  # Find the workbook if it's already open
                    break

            if not workbook:
                workbook = self.excel.Workbooks.Open(file_path)  # Open the workbook if it's not already open

            sheet = workbook.Worksheets(1)  # Get the first worksheet
            
            # Format all cells in the sheet as text
            sheet.Cells.NumberFormat = "@"

            for i, row in enumerate(self.mydata, start=1):
                for j, value in enumerate(row, start=1):
                    cell = sheet.Cells(i, j)
                    cell.NumberFormat = "@"  # Format all cells as text
                    if j == 2 and value.startswith("'"):  # Roll number column
                        cell.Value = value[1:]  # Remove the leading single quote
                    else:
                        cell.Value = value  # Set the cell value

            workbook.Save()  # Save the workbook
            print(f"Updated Excel file: {file_path}")  # Print confirmation message

        except Exception as e:
            print(f"Error updating Excel: {str(e)}")  # Print error message if Excel update fails
        finally:
            if workbook:
                workbook.Close()  # Close the workbook
            pythoncom.CoUninitialize()  # Uninitialize COM library

    def show_loading_animation(self):
        self.loading_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#2c2c2c")  # Create a frame for loading animation
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.3, relheight=0.3)  # Place the loading frame

        loading_label = ctk.CTkLabel(self.loading_frame, text="Updating...", font=("Roboto", 18, "bold"), text_color="#ffffff")  # Create a label for loading text
        loading_label.pack(pady=20)  # Pack the loading label

        self.canvas = tk.Canvas(self.loading_frame, width=100, height=100, bg="#2c2c2c", highlightthickness=0)  # Create a canvas for loading animation
        self.canvas.pack(pady=10)  # Pack the canvas

        self.create_loading_circles()  # Create loading circles
        self.animate_loading()  # Start the loading animation

    def create_loading_circles(self):
        self.circles = []
        colors = ["#4CAF50", "#2196F3", "#FFC107", "#E91E63"]  # Colors for the loading circles
        for i in range(8):
            angle = i * (360 / 8)
            x = 50 + 35 * math.cos(math.radians(angle))
            y = 50 + 35 * math.sin(math.radians(angle))
            circle = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=colors[i % len(colors)], outline="")  # Create a circle
            self.circles.append(circle)  # Add the circle to the list

    def animate_loading(self):
        for i, circle in enumerate(self.circles):
            self.canvas.itemconfig(circle, state="normal" if i == 0 else "hidden")  # Show only the first circle initially
        self.root.after(100, self.rotate_circles)  # Start rotating the circles after a short delay

    def rotate_circles(self):
        if not hasattr(self, 'loading_frame'):
            return  # Stop the animation if the loading frame has been destroyed
        states = [self.canvas.itemcget(circle, "state") for circle in self.circles]  # Get the current states of circles
        states = states[1:] + states[:1]  # Rotate the states
        for circle, state in zip(self.circles, states):
            self.canvas.itemconfig(circle, state=state)  # Update the states of circles
        self.root.after(100, self.rotate_circles)  # Continue the rotation after a short delay

    def show_success_message(self):
        self.hide_loading_animation()  # Hide the loading animation
        messagebox.showinfo("Success", "Attendance updated successfully", parent=self.root)  # Show success message

    def show_not_found_message(self):
        self.hide_loading_animation()  # Hide the loading animation
        messagebox.showwarning("Not Found", "No matching record found to update", parent=self.root)  # Show warning message

    def hide_loading_animation(self):
        if hasattr(self, 'loading_frame'):
            self.loading_frame.destroy()  # Destroy the loading frame
            delattr(self, 'loading_frame')  # Remove the loading_frame attribute

    def __del__(self):
        if self.excel:
            self.excel.Quit()  # Quit Excel application
            del self.excel  # Delete Excel application instance

    def update_csv_file(self):
        with open(self.current_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.mydata)

if __name__ == "__main__":
    root = ctk.CTk()  # Create the main window
    obj = Attendance(root)  # Create an instance of the Attendance class
    root.mainloop()  # Start the main event loop
