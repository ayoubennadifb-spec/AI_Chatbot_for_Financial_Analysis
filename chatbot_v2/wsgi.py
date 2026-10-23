"""
Gunicorn WSGI entry point
=========================
Production run:
    gunicorn wsgi:app --workers 4 --bind 0.0.0.0:5001 --timeout 120

Workers:
    - 4 workers = handles 4 concurrent requests
    - Each worker is a separate process (not affected by Python GIL)
    - Rule of thumb: 2 * CPU_cores + 1
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()
