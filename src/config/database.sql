CREATE DATABASE IF NOT EXISTS face_recognizer;
USE face_recognizer;

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
); 