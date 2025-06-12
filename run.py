#!/usr/bin/env python3
"""
Launcher script for the GUI Automation Tool.
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from app.main import main

if __name__ == '__main__':
    main()
