import os
import shutil

def create_directories():
    directories = [
        'src/core',
        'src/gui',
        'src/utils',
        'src/data',
        'src/models',
        'src/config',
        'src/logs',
        'src/static/images'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def move_files():
    # Move core files
    shutil.move('face_recognition.py', 'src/core/face_recognition.py')
    shutil.move('train.py', 'src/core/train.py')
    
    # Move GUI files
    shutil.move('app_launcher.py', 'src/gui/app_launcher.py')
    shutil.move('loginpage.py', 'src/gui/loginpage.py')
    shutil.move('loginpage2.py', 'src/gui/loginpage2.py')
    shutil.move('student.py', 'src/gui/student.py')
    shutil.move('attendance.py', 'src/gui/attendance.py')
    shutil.move('help_chatbot.py', 'src/gui/help_chatbot.py')
    shutil.move('main.py', 'src/gui/main.py')
    
    # Move data files
    if os.path.exists('DATA'):
        shutil.move('DATA', 'src/data/student_photos')
    shutil.move('Test1.csv', 'src/data/Test1.csv')
    shutil.move('Test2.csv', 'src/data/Test2.csv')
    shutil.move('EIP2.csv', 'src/data/EIP2.csv')
    
    # Move model files
    shutil.move('classifier.xml', 'src/models/classifier.xml')
    shutil.move('haarcascade_frontalface_default.xml', 'src/models/haarcascade_frontalface_default.xml')
    
    # Move config files
    shutil.move('face_recognizer.sql', 'src/config/face_recognizer.sql')
    shutil.move('chatbot_window_size.txt', 'src/config/chatbot_window_size.txt')
    
    # Move images
    if os.path.exists('Image'):
        for file in os.listdir('Image'):
            shutil.move(f'Image/{file}', f'src/static/images/{file}')
        os.rmdir('Image')
    
    # Move logs
    shutil.move('student_management.log', 'src/logs/student_management.log')

def update_imports():
    # Update import statements in all Python files
    for root, _, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update imports
                content = content.replace('from student import', 'from gui.student import')
                content = content.replace('from train import', 'from core.train import')
                content = content.replace('from face_recognition import', 'from core.face_recognition import')
                content = content.replace('from attendance import', 'from gui.attendance import')
                content = content.replace('from help_chatbot import', 'from gui.help_chatbot import')
                content = content.replace('from loginpage import', 'from gui.loginpage import')
                content = content.replace('from loginpage2 import', 'from gui.loginpage2 import')
                
                # Update file paths
                content = content.replace(r'Image\\', r'static/images/')
                content = content.replace(r'DATA\\', r'data/student_photos/')
                content = content.replace('classifier.xml', 'models/classifier.xml')
                content = content.replace('haarcascade_frontalface_default.xml', 'models/haarcascade_frontalface_default.xml')
                content = content.replace('face_recognizer.sql', 'config/face_recognizer.sql')
                content = content.replace('chatbot_window_size.txt', 'config/chatbot_window_size.txt')
                content = content.replace('student_management.log', 'logs/student_management.log')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

if __name__ == '__main__':
    create_directories()
    move_files()
    update_imports() 