# This file makes the utils directory a Python package
# It can be empty, but we'll add a version number for good practice
__version__ = '1.0.0'

"""
Utility functions for SmartAttend Pro
"""

from .paths import get_model_path, get_image_path, get_data_file_path, ensure_directories_exist

__all__ = ['get_model_path', 'get_image_path', 'get_data_file_path', 'ensure_directories_exist'] 