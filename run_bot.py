#!/usr/bin/env python3
"""
Run script for the Telegram Finance Tracker Bot
This script ensures the bot runs from the correct directory
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the bot
from bot import main

if __name__ == '__main__':
    main()
