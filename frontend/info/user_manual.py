"""
User Manual Component
Provides access to user documentation
"""

import tkinter as tk
from tkinter import messagebox
import os
from ..utils.styles import Colors, Fonts


class UserManual:
    """Component for accessing user manual."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the user manual component.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
    
    def create(self):
        """Create the user manual UI."""
        main_frame = tk.LabelFrame(
            self.parent,
            text="📖 User Manual",
            font=Fonts.HEADER,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.X, padx=10, pady=10)
        
        container = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        container.pack(fill=tk.X, padx=20, pady=15)
        
        desc_label = tk.Label(
            container,
            text="Access the comprehensive Welvision User Manual with detailed instructions and\ntroubleshooting guides",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            justify=tk.LEFT
        )
        desc_label.pack(anchor=tk.W, pady=(0, 15))
        
        tk.Button(
            container,
            text="📄 Open User Manual",
            font=Fonts.TEXT_BOLD,
            bg="#28A745",
            fg=Colors.WHITE,
            activebackground="#218838",
            activeforeground=Colors.WHITE,
            command=self.open_user_manual,
            width=20,
            cursor="hand2"
        ).pack(anchor=tk.W)
    
    def open_user_manual(self):
        """Open the user manual PDF."""
        try:
            manual_path = "User_Manual.pdf"
            
            if os.path.exists(manual_path):
                os.startfile(manual_path)
            else:
                messagebox.showwarning(
                    "Manual Not Found",
                    f"User manual not found at:\n{os.path.abspath(manual_path)}\n\n"
                    "Please contact the administrator."
                )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to open user manual:\n{str(e)}"
            )
