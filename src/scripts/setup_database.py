import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Set up the database and required tables for the face recognition system."""
    try:
        # First connect without database to create it if not exists
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
            cursor.execute(f"USE {os.getenv('DB_NAME')}")
            
            # Create student table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student (
                    Dep VARCHAR(50),
                    Branch VARCHAR(50),
                    Semester VARCHAR(20),
                    Student_id VARCHAR(20) PRIMARY KEY,
                    Name VARCHAR(100),
                    Division VARCHAR(20),
                    Roll VARCHAR(20),
                    Gender VARCHAR(20),
                    Dob DATE,
                    Email VARCHAR(100),
                    Phone VARCHAR(20),
                    Address TEXT,
                    PhotoSample VARCHAR(10) DEFAULT 'No'
                )
            """)
            
            # Create attendance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    Student_id VARCHAR(20),
                    Name VARCHAR(100),
                    Department VARCHAR(50),
                    Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Date DATE,
                    Attendance_status VARCHAR(10),
                    FOREIGN KEY (Student_id) REFERENCES student(Student_id)
                )
            """)
            
            print("Database setup completed successfully!")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database() 