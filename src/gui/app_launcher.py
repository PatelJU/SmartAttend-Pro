import tkinter as tk
import sys
from tkinter import ttk

print(f"Python version: {sys.version}")
print(f"Tkinter version: {tk.TkVersion}")

from gui.loginpage import login_process
from main import Face_Recognition

def launch_main_app():
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.state('zoomed')  # This will maximize the window
    
    style = ttk.Style(root)
    style.theme_use('clam')  # You can try different themes like 'alt', 'default', 'classic'
    
    def resize_window(event):
        if event.widget == root:
            app.root.geometry(f"{event.width}x{event.height}+0+0")
    
    root.bind("<Configure>", resize_window)
    
    app = Face_Recognition(root)
    
    # Force update of geometry
    root.update_idletasks()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.state('zoomed')
    
    return root  # Return the root window

def launch_app():
    if login_process():
        print("Login successful!")
        root = launch_main_app()
        root.mainloop()
    else:
        print("Login failed or cancelled.")

if __name__ == "__main__":
    root = None
    try:
        launch_app()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Add this to clean up any remaining after callbacks
        if root:
            for after_id in root.tk.call('after', 'info'):
                root.after_cancel(after_id)
        else:
            print("Root window was not created, skipping cleanup.")
