#!/usr/bin/env python3
"""
Runner script for Crowd Due Dill - AI Agent for Crowdfunding Regulation & Legal Compliance
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

if __name__ == "__main__":
    from main import run_chatbot
    run_chatbot() 