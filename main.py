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
    try:
        # Import with proper error handling
        from cli.app import main  # type: ignore
        main()
    except ImportError as e:
        print(f"Error importing CLI application: {e}")
        print("Please ensure the src/cli/app.py file exists and is properly configured.")
        print("You can also run the CLI directly with: python src/cli/app.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)