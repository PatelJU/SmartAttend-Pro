import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import inspect
import os
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont

class HelpChatbot:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app
        self.questions_answers = self.generate_qa()

        self.chatbot_window = None
        self.chat_text = None
        self.chat_frame = None

    def generate_qa(self):
        qa = [
            ("How do I start the face recognition process?", "To start face recognition, click the 'Face Detect' button on the main screen. This will open the camera and begin detecting faces."),
            ("How to begin face detection?", "To begin face detection, click the 'Face Detect' button on the main screen. This will activate the camera and start the face recognition process."),
            ("How do I add a new student?", "To add a new student:\n1. Click the 'Student Details' button\n2. Fill in the student's information in the form\n3. Click 'Take Photo Sample' to capture the student's photos\n4. Click 'Save' to add the student to the database"),
            ("Adding a new student", "To add a new student:\n1. Click 'Student Details'\n2. Enter the student's information\n3. Use 'Take Photo Sample' to capture photos\n4. Click 'Save' to add to the database"),
            ("How do I update a student's photo?", "To update a student's photo:\n1. Go to 'Student Details'\n2. Search for the student using their ID or name\n3. Click on their record to select it\n4. Click 'Update Photo Sample' to capture new photos"),
            ("Updating student photos", "To update a student's photos:\n1. Navigate to 'Student Details'\n2. Find the student by ID or name\n3. Select their record\n4. Click 'Update Photo Sample' for new photos"),
            ("How does attendance logging work?", "Attendance is automatically logged when a student's face is recognized during the face detection process. The attendance data is saved to a CSV file."),
            ("Attendance logging process", "Attendance is recorded automatically when the system recognizes a student's face during face detection. This data is then saved in a CSV file."),
            ("How can I view the attendance records?", "To view attendance records:\n1. Click the 'Attendance' button on the main screen\n2. You can import a CSV file of attendance records\n3. Use the search and filter options to find specific records"),
            ("Viewing attendance data", "To access attendance records:\n1. Click 'Attendance' on the main screen\n2. Import a CSV file with attendance data\n3. Use search and filter features to find specific entries"),
            ("What does the 'Train Data' button do?", "The 'Train Data' button trains the face recognition model on the current set of student photos. Use this after adding new students or updating photos."),
            ("Purpose of 'Train Data' button", "The 'Train Data' button updates the face recognition model with the latest student photos. Use it after adding new students or updating existing photos."),
            ("How do I search for a student?", "In the 'Student Details' section, you can use the search bar at the top to find students by their ID, name, or other details."),
            ("Searching for students", "To find a student, go to the 'Student Details' section and use the search bar at the top. You can search by ID, name, or other information."),
            ("Can I export attendance data?", "Yes, in the 'Attendance' section, you can export the displayed attendance data to a CSV file using the 'Export CSV' button."),
            ("Exporting attendance records", "Yes, you can export attendance data. In the 'Attendance' section, use the 'Export CSV' button to save the displayed records as a CSV file."),
            ("How do I close the application?", "To close the application, click the 'Exit' button on the main screen or use the window's close button."),
            ("Closing the app", "To exit the application, either click the 'Exit' button on the main screen or use the window's close button."),
            ("What should I do if face recognition isn't working?", "If face recognition isn't working:\n1. Ensure proper lighting\n2. Make sure the student is facing the camera\n3. Try updating the student's photos\n4. Retrain the data using the 'Train Data' button"),
            ("Troubleshooting face recognition", "If face recognition is not working:\n1. Check the lighting conditions\n2. Ensure the student faces the camera directly\n3. Update the student's photos\n4. Use the 'Train Data' button to retrain the system"),
        ]
        return qa

    def show_chatbot(self, parent):
        self.chatbot_window = parent
        self.chatbot_window.title("Help Chatbot")
        self.chatbot_window.geometry("900x700")

        # Create a paned window for split view
        paned_window = ttk.PanedWindow(self.chatbot_window, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left frame for questions
        left_frame = ctk.CTkFrame(paned_window, corner_radius=0)
        paned_window.add(left_frame, weight=1)

        question_label = ctk.CTkLabel(left_frame, text="Common Questions", font=("Roboto", 18, "bold"))
        question_label.pack(pady=10)

        self.question_listbox = tk.Listbox(left_frame, font=("Roboto", 14), bg="#2c2c2c", fg="white", selectbackground="#4a4a4a")
        self.question_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for i, (question, _) in enumerate(self.questions_answers, 1):
            self.question_listbox.insert(tk.END, f"{i}. {question}")
        self.question_listbox.bind("<<ListboxSelect>>", self.on_question_select)

        # Right frame for chat
        right_frame = ctk.CTkFrame(paned_window, corner_radius=0)
        paned_window.add(right_frame, weight=2)

        # Chat display
        self.chat_frame = ctk.CTkFrame(right_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        self.chat_text = tk.Text(self.chat_frame, wrap=tk.WORD, font=("Roboto", 14), bg="#F0F0F0", relief=tk.FLAT)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_text.config(state=tk.DISABLED)

        # Scrollbar for chat
        scrollbar = ctk.CTkScrollbar(self.chat_frame, command=self.chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.configure(yscrollcommand=scrollbar.set)

        # Input frame
        input_frame = ctk.CTkFrame(right_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.user_input = ctk.CTkEntry(input_frame, font=("Roboto", 14), placeholder_text="Type your question here...")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        send_button = ctk.CTkButton(input_frame, text="Send", command=self.process_input, width=100, font=("Roboto", 14))
        send_button.pack(side=tk.RIGHT)

        self.user_input.bind("<Return>", lambda event: self.process_input())

        # Welcome message
        instructions = (
            "Welcome to the Help Chatbot!\n\n"
            "You can ask questions in the following ways:\n"
            "1. Type a question or keywords in the input box\n"
            "2. Enter the number of a question from the list\n"
            "3. Select a question from the list on the left\n\n"
            "The chatbot will try to match your input to the most relevant question and provide an answer.\n"
        )
        self.add_message(instructions, is_user=False)

    def on_question_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            question, answer = self.questions_answers[index]
            self.update_chat(f"You: {question}\n\nChatbot: {answer}\n\n")

    def process_input(self):
        user_text = self.user_input.get().strip().lower()
        matched_question = None

        if user_text.isdigit() and 1 <= int(user_text) <= len(self.questions_answers):
            matched_question = self.questions_answers[int(user_text) - 1]
        else:
            for i, (question, answer) in enumerate(self.questions_answers, 1):
                if user_text in question.lower():
                    matched_question = (question, answer)
                    break

        if matched_question:
            question, answer = matched_question
            self.update_chat(f"You: {question}\n\nChatbot: {answer}\n\n")
        else:
            self.update_chat(f"You: {user_text}\n\nChatbot: I'm sorry, I don't have an answer for that specific question. Please try selecting one of the questions from the list on the left or rephrase your question.\n\n")
        
        self.user_input.delete(0, tk.END)

    def update_chat(self, message):
        parts = message.split("\n\n")
        if len(parts) >= 2:
            user_message = parts[0]
            chatbot_message = "\n\n".join(parts[1:])
            self.add_message(user_message[4:], is_user=True)
            self.add_message(chatbot_message[9:], is_user=False)
        else:
            self.add_message(message, is_user=False)

    def on_canvas_configure(self, event):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def on_frame_configure(self, event):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def add_message(self, message, is_user=True):
        frame = ctk.CTkFrame(self.chat_text, fg_color="transparent")
        frame.pack(padx=10, pady=5, anchor="e" if is_user else "w", fill="x")

        if is_user:
            bubble_color = "#007AFF"  # iOS blue for user messages
            text_color = "white"
            anchor = "e"
        else:
            bubble_color = "#E5E5EA"  # iOS gray for chatbot messages
            text_color = "black"
            anchor = "w"

        # Ensure each line starts on a new line
        formatted_message = "\n".join(line.strip() for line in message.split("\n"))

        message_bubble = ctk.CTkLabel(
            frame,
            text=formatted_message,
            font=("Roboto", 14),
            text_color=text_color,
            fg_color=bubble_color,
            corner_radius=15,
            anchor=anchor,
            justify="left",
            wraplength=400
        )
        message_bubble.pack(side="right" if is_user else "left", padx=5, pady=5)

        self.chat_text.window_create(tk.END, window=frame)
        self.chat_text.insert(tk.END, "\n")
        self.chat_text.see(tk.END)
        self.chat_text.update_idletasks()


