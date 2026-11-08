"""
Input Fields Module
Email and password input components
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class InputFields:
    """Email and password input fields."""
    
    def __init__(self, parent):
        """
        Initialize the input fields.
        
        Args:
            parent: Parent frame to contain the input fields
        """
        self.parent = parent
        self.email_entry = None
        self.password_entry = None
        
    def create(self):
        """
        Create email and password input fields.
        
        Returns:
            tuple: (email_entry, password_entry) Entry widgets
        """
        self._create_email_field()
        
        self._create_password_field()
        
        return self.email_entry, self.password_entry
    
    def _create_email_field(self):
        """Create the email input field."""
        email_label = tk.Label(
            self.parent, 
            text="Email", 
            font=Fonts.TEXT_BOLD, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK, 
            anchor="w"
        )
        email_label.pack(fill="x", pady=(0, 8), padx=10)
        
        self.email_entry = tk.Entry(
            self.parent, 
            font=Fonts.TEXT, 
            width=50,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.email_entry.pack(pady=(0, 25), ipady=10)
    
    def _create_password_field(self):
        """Create the password input field."""
        password_label = tk.Label(
            self.parent, 
            text="Password", 
            font=Fonts.TEXT_BOLD, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK, 
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 8), padx=10)
        
        self.password_entry = tk.Entry(
            self.parent, 
            font=Fonts.TEXT, 
            width=50,
            show="*",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.password_entry.pack(pady=(0, 40), ipady=10)
    
    def get_credentials(self):
        """
        Get the entered credentials.
        
        Returns:
            tuple: (email, password) as strings
        """
        try:
            if self.email_entry and self.email_entry.winfo_exists():
                email = self.email_entry.get().strip()
            else:
                email = ""
            
            if self.password_entry and self.password_entry.winfo_exists():
                password = self.password_entry.get().strip()
            else:
                password = ""
            
            return email, password
        except tk.TclError:
            return "", ""
