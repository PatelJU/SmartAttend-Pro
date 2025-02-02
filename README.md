# SmartAttend Pro

<div align="center">

![SmartAttend Pro](.github/assets/main_dashboard.png)

A modern face recognition-based attendance system built with Python and OpenCV, featuring a sleek dark-themed UI.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MySQL](https://img.shields.io/badge/MySQL-Latest-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

## 🌟 Key Features

### 1. Student Management
<div align="center">
  <img src=".github/assets/student_management.png" alt="Student Management Interface" width="800"/>
</div>

- 📝 Complete student information management
- 🏢 Department and branch-wise organization
- 📸 Photo sample collection for face recognition
- 🔍 Intuitive search and filter capabilities
- 📤 Bulk import/export functionality

### 2. Face Recognition
- 🎯 Real-time face detection and recognition
- ✨ High-accuracy student identification
- 📊 Confidence level indicators
- ✅ Automatic attendance marking
- 👥 Multi-face detection support

### 3. Attendance Management
<div align="center">
  <img src=".github/assets/attendance_management.png" alt="Attendance Management Interface" width="800"/>
</div>

- ⏰ Automated attendance tracking
- 📊 CSV import/export functionality
- 🔄 Real-time attendance status updates
- 📋 Detailed attendance records
- 💼 Easy data management

### 4. Training System
<div align="center">
  <img src=".github/assets/train_data.png" alt="Training Interface" width="800"/>
</div>

- 🧠 Neural network-based training
- 📈 Progress visualization
- 📊 Real-time accuracy metrics
- 🔄 Automated model optimization
- 📁 Dataset management

### 5. Help System
<div align="center">
  <img src=".github/assets/help_chatbot.png" alt="Help System Interface" width="800"/>
</div>

- 💬 Interactive help chatbot
- ❓ Common questions and answers
- 📝 Step-by-step guides
- 🔍 Quick issue resolution
- 🎯 User-friendly interface

## 🛠️ Technical Features

- 🎨 Modern dark-themed UI using CustomTkinter
- 👁️ Real-time face detection using OpenCV
- 🗄️ MySQL database integration
- 🔄 Multi-threaded processing
- 📊 CSV data import/export
- 🔒 Secure authentication system
- 💾 Automated backup system

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/PatelJU/SmartAttend-Pro.git
cd SmartAttend-Pro
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python src/scripts/setup_database.py
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## 🚀 Usage

1. Start the application:
```bash
python src/app.py
```

2. Navigate through the modules:
   - 👥 Student Details: Manage student information
   - 👁️ Face Detect: Start face recognition
   - ✅ Attendance: View and manage attendance
   - 🧠 Train Data: Train the recognition model
   - 📸 Photos: View captured photos

## 💻 System Requirements

- Python 3.8+
- OpenCV with contrib modules
- MySQL/MariaDB
- Webcam

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV team for face recognition modules
- CustomTkinter for modern UI components
- All contributors who have helped with testing and improvements

## 📞 Contact

- Project Link: [https://github.com/PatelJU/SmartAttend-Pro](https://github.com/PatelJU/SmartAttend-Pro) 
