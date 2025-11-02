#!/usr/bin/env python3
"""
ArXiv Research Assistant - Main Entry Point

This is a convenience wrapper that calls the main CLI application.
The actual implementation is in src/cli/app.py
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
if __name__ == "__main__":
    from cli.app import main
    main()