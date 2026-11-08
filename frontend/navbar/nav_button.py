"""
Navigation Button Component
Individual button component for the navigation bar
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class NavButton:
    """Individual navigation button component."""
    
    def __init__(self, parent, text, command, button_id):
        """
        Initialize a navigation button.
        
        Args:
            parent: Parent frame
            text: Button text
            command: Callback function when clicked
            button_id: Unique identifier for the button
        """
        self.parent = parent
        self.text = text
        self.command = command
        self.button_id = button_id
        self.button = None
        self.is_active = False
        
        self.inactive_bg = "#2563a8"
        self.active_bg = "#28a745"
        self.hover_bg = "#3a7bc8"
        self.text_color = Colors.WHITE
        
    def create(self):
        """Create the button widget."""
        self.button = tk.Button(
            self.parent,
            text=self.text,
            font=Fonts.SMALL_BOLD,
            bg=self.inactive_bg,
            fg=self.text_color,
            activebackground=self.hover_bg,
            activeforeground=self.text_color,
            disabledforeground=self.text_color,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self._on_click
        )
        
        self.button.bind("<Enter>", self._on_hover)
        self.button.bind("<Leave>", self._on_leave)
        
        return self.button
    
    def _on_click(self):
        """Handle button click."""
        if self.command:
            self.command(self.button_id)
    
    def _on_hover(self, event):
        """Handle mouse hover."""
        if self.button['state'] == tk.DISABLED:
            return
        if not self.is_active:
            self.button.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        if self.button['state'] == tk.DISABLED:
            return
        if not self.is_active:
            self.button.config(bg=self.inactive_bg)
    
    def set_active(self, active=True):
        """
        Set the active state of the button.
        
        Args:
            active: Boolean indicating if button is active
        """
        self.is_active = active
        if active:
            self.button.config(bg=self.active_bg)
        else:
            self.button.config(bg=self.inactive_bg)
    
    def pack(self, **kwargs):
        """Pack the button with the given kwargs."""
        if self.button:
            self.button.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the button with the given kwargs."""
        if self.button:
            self.button.grid(**kwargs)
