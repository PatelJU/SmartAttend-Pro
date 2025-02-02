"""
Pytest configuration file with shared fixtures.
"""
import os
import pytest
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def db_connection():
    """Create a test database connection."""
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "face_recognition_db")
    )
    yield connection
    connection.close()

@pytest.fixture(scope="session")
def db_cursor(db_connection):
    """Create a test database cursor."""
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()

@pytest.fixture(scope="function")
def cleanup_database(db_connection, db_cursor):
    """Clean up the test database after each test."""
    yield
    tables = ["attendance", "students", "users"]
    for table in tables:
        db_cursor.execute(f"DELETE FROM {table}")
    db_connection.commit() 