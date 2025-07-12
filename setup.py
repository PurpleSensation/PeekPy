"""
Setup configuration for PeekPy package.
"""
from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "CoreMarine Utilities Package for maritime structural monitoring applications."

# Get version from __init__.py
def get_version():
    try:
        with open("PeekPy/__init__.py", "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except:
        return "1.0.0"

setup(
    name="peekpy",
    version=get_version(),
    author="Dr. Hono Salval",
    author_email="hono.salval@coremarine.com",
    description="Professional utilities for maritime structural monitoring applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/core-marine-dev/PeekPy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "full": [
            "pygments>=2.10.0",
            "matplotlib>=3.3.0",
        ],
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
