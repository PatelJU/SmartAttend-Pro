from setuptools import setup, find_packages

setup(
    name="smartattend-pro",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'opencv-contrib-python>=4.8.0',
        'numpy>=1.24.0',
        'Pillow>=10.0.0',
        'customtkinter>=5.2.0',
        'mysql-connector-python>=8.0.33',
        'python-dotenv>=1.0.0',
        'pandas>=2.0.0',
        'tqdm>=4.65.0',
        'scikit-learn>=1.3.0',
    ],
    python_requires='>=3.8',
    author="PatelJU",
    description="A modern face recognition-based attendance system",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PatelJU/SmartAttend-Pro",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 