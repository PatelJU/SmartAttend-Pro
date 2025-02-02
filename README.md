# SmartAttend Pro

A modern face recognition-based attendance system built with Python and OpenCV.

## Features

- Real-time face detection and recognition
- Automatic attendance marking
- Modern dark-themed UI
- Database integration for student information
- CSV export for attendance records
- Multi-threaded processing for smooth performance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/PatelJU/SmartAttend-Pro.git
cd SmartAttend-Pro
```

2. Create and activate a virtual environment (recommended):
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
# Copy example env file
cp .env.example .env
# Edit .env with your database credentials and other settings
```

## Usage

1. Start the application:
```bash
python src/app.py
```

2. Use the interface to:
   - Manage student records
   - Start face recognition
   - View attendance records
   - Generate reports

## System Requirements

- Python 3.8+
- OpenCV with contrib modules
- MySQL/MariaDB
- Webcam

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV team for face recognition modules
- CustomTkinter for modern UI components
- All contributors who have helped with testing and improvements

## Contact

- Project Link: [https://github.com/PatelJU/SmartAttend-Pro](https://github.com/PatelJU/SmartAttend-Pro) 