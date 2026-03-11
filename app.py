# ============================================================
#  NanoBio Studio  Connecting Nanotechnology & Biotechnology
# Developed by Experts Group FZE
#
# ENTRY POINT WRAPPER - Routes to modern biotech-lab-main/App.py
# This file ensures Streamlit Cloud deployments work correctly
# ============================================================

import sys
import os
from pathlib import Path

# Add biotech-lab-main to path so it can be imported
biotech_path = Path(__file__).parent / "biotech-lab-main"
sys.path.insert(0, str(biotech_path))

# Import and run the modern App
from App import *
