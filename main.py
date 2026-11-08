"""
WELVISION - Automated Roller Defect Inspection System
Main Entry Point

This is the main entry point for the WelVision application.
It initializes and runs the GUI application.

Author: Welvision Team
Date: October 2025
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.app import WelVisionApp


def main():
    """Main entry point for the application."""  
    try:
        app = WelVisionApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
