"""
SmartAttend Pro - A modern face recognition-based attendance system
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import paths module to ensure directories are created
from src.utils.paths import ensure_directories_exist

# Create all necessary directories
ensure_directories_exist()

# Import version
__version__ = '1.0.0' 