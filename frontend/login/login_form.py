"""
Login Form Container Module
Handles the main form layout and structure
"""

import tkinter as tk
from ..utils.styles import Colors


class LoginForm:
    """Main login form container."""
    
    def __init__(self, parent):
        """
        Initialize the login form container.
        
        Args:
            parent: Parent Tk window
        """
        self.parent = parent
        self.frame = None
        self.container = None
        
    def create(self):
        """
        Create the main login form container.
        
        Returns:
            container: The inner container frame for form components
        """
        self.frame = tk.Frame(
            self.parent, 
            bg=Colors.BLACK,
            width=450,
            height=575
        )
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.frame.pack_propagate(False)
        
        self.container = tk.Frame(self.frame, bg=Colors.BLACK)
        self.container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        return self.container
    
    def destroy(self):
        """Destroy the login form."""
        if self.frame:
            self.frame.destroy()
            self.frame = None
            self.container = None
