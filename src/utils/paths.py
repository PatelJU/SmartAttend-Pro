import os

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define all important paths
LOGS_DIR = os.path.join(PROJECT_ROOT, 'src', 'logs')
DATA_DIR = os.path.join(PROJECT_ROOT, 'src', 'data')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'src', 'models')
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'src', 'config')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'src', 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
STUDENT_PHOTOS_DIR = os.path.join(DATA_DIR, 'student_photos')

def ensure_directories_exist():
    """Ensure all required directories exist"""
    directories = [
        LOGS_DIR,
        DATA_DIR,
        MODELS_DIR,
        CONFIG_DIR,
        STATIC_DIR,
        IMAGES_DIR,
        STUDENT_PHOTOS_DIR
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_log_file_path():
    """Get the path to the log file"""
    return os.path.join(LOGS_DIR, 'student_management.log')

def get_model_path(model_name):
    """Get the path to a model file"""
    return os.path.join(MODELS_DIR, model_name)

def get_config_path(config_name):
    """Get the path to a config file"""
    return os.path.join(CONFIG_DIR, config_name)

def get_image_path(image_name):
    """Get the path to an image file"""
    return os.path.join(IMAGES_DIR, image_name)

def get_data_file_path(file_name):
    """Get the path to a data file"""
    return os.path.join(DATA_DIR, file_name)

# Create all directories when the module is imported
ensure_directories_exist() 