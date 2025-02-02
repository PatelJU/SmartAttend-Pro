from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Read README for long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="smartattend-pro",
    version="1.0.0",
    author="PatelJU",
    description="A modern face recognition attendance system with an intuitive UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PatelJU/SmartAttend-Pro",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=required,
    entry_points={
        "console_scripts": [
            "smartattend=app:main",
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/PatelJU/SmartAttend-Pro/issues",
        "Source": "https://github.com/PatelJU/SmartAttend-Pro",
    },
) 