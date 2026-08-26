#!/usr/bin/env python3
"""
ATS Matrix PC Cleaner
=====================
Professional Windows PC optimization tool.
Cleans temporary files, browser caches, prefetch, recycle bin and more
with a modern dark-themed interface.

Run:
    python main.py

Requirements:
    pip install -r requirements.txt
"""

import sys
import platform

def main():
    if platform.system() != "Windows":
        print("⚠  ATS Matrix PC Cleaner is primarily designed for Windows.")
        print("   Limited functionality may be available on other platforms.")
        # still allow run

    try:
        from cleaner.ui import run_app
        run_app()
    except ImportError as e:
        print("Missing dependency. Please install requirements:")
        print("    pip install -r requirements.txt")
        print(f"\nDetails: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
