import os
import sys
import logging
import tkinter as tk
import customtkinter as ctk
from gui.main import Face_Recognition
from utils.paths import get_log_file_path, ensure_directories_exist

def setup_logging():
    """Set up logging configuration"""
    ensure_directories_exist()
    logging.basicConfig(
        filename=get_log_file_path(),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point of the application"""
    try:
        # Set up logging
        setup_logging()
        
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create the main window
        root = ctk.CTk()
        app = Face_Recognition(root)
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 