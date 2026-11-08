"""
Progress Window Component
Simple progress window for long operations
"""

import tkinter as tk
from ..utils.styles import Fonts


class ProgressWindow:
    """Simple progress window for displaying operation status."""
    
    def __init__(self, parent, message):
        """
        Create a progress window.
        
        Args:
            parent: Parent widget
            message: Progress message to display
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Please Wait")
        self.window.geometry("300x100")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.window.winfo_screenheight() // 2) - (100 // 2)
        self.window.geometry(f"300x100+{x}+{y}")
        
        label = tk.Label(
            self.window,
            text=message,
            font=Fonts.TEXT,
            pady=30
        )
        label.pack()
    
    def close(self):
        """Close the progress window."""
        self.window.destroy()
