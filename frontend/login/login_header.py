"""
Login Header Module
Contains logo and subtitle components
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class LoginHeader:
    """Login page header with logo and subtitle."""
    
    @staticmethod
    def create(parent):
        """
        Create the header section with logo and subtitle.
        
        Args:
            parent: Parent frame to contain the header
        """
        logo_label = tk.Label(
            parent, 
            text="WELVISION", 
            font=Fonts.TITLE, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK
        )
        logo_label.pack(pady=(20, 10))
        
        subtitle_label = tk.Label(
            parent, 
            text="Please sign in to continue", 
            font=Fonts.LABEL, 
            fg=Colors.WHITE, 
            bg=Colors.BLACK
        )
        subtitle_label.pack(pady=(0, 40))
