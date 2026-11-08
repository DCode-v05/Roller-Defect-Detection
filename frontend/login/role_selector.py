"""
Role Selector Module
Radio button component for role selection
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class RoleSelector:
    """Role selection component with radio buttons."""
    
    def __init__(self, parent):
        """
        Initialize the role selector.
        
        Args:
            parent: Parent frame to contain the role selector
        """
        self.parent = parent
        self.role_var = tk.StringVar(value="Operator")
        
    def create(self):
        """
        Create the role selection radio buttons.
        
        Returns:
            role_var: StringVar containing the selected role
        """
        role_frame = tk.Frame(self.parent, bg=Colors.BLACK)
        role_frame.pack(pady=(0, 30))
        
        radio_container = tk.Frame(role_frame, bg=Colors.BLACK)
        radio_container.pack()
        
        roles = [
            ("Operator", "Operator"),
            ("Admin", "Admin"),
            ("Super Admin", "Super Admin")
        ]
        
        for text, value in roles:
            rb = tk.Radiobutton(
                radio_container, 
                text=text, 
                variable=self.role_var, 
                value=value,
                font=Fonts.TEXT, 
                fg=Colors.WHITE, 
                bg=Colors.BLACK, 
                selectcolor=Colors.BLACK,
                activebackground=Colors.BLACK,
                activeforeground=Colors.WHITE,
                highlightthickness=0
            )
            rb.pack(side=tk.LEFT, padx=15)
        
        return self.role_var
