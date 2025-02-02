import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration using environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "face_recognition_db")
}

def setup_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS face_recognizer")
            cursor.execute("USE face_recognizer")
            
            # Create student table
            create_table_query = """
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
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Database and table created successfully!")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database() 