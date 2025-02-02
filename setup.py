from setuptools import setup, find_packages

setup(
    name="smartattend-pro",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'opencv-python-headless',
        'numpy',
        'pillow',
        'customtkinter',
        'python-dotenv',
        'mysql-connector-python',
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