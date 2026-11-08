"""
User Actions Module
Handles CRUD operations with confirmation dialogs
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts


class UserActions:
    """User action buttons and operations."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize user actions.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to UserManagementTab instance
        """
        self.parent = parent
        self.tab = tab_instance
    
    def create(self):
        """Create action buttons."""
        actions_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        actions_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        button_config = {
            'font': ("Arial", 11, "bold"),
            'cursor': 'hand2',
            'width': 15,
            'height': 1,
            'pady': 8
        }
        
        add_btn = tk.Button(
            actions_frame,
            text="➕ Add New User",
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            command=self.tab.add_user,
            **button_config
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        read_btn = tk.Button(
            actions_frame,
            text="📖 Read User",
            bg=Colors.PRIMARY_BLUE,
            fg=Colors.WHITE,
            command=self.tab.read_user,
            **button_config
        )
        read_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(
            actions_frame,
            text="🔄 Update User",
            bg=Colors.INFO,
            fg=Colors.WHITE,
            command=self.tab.update_user,
            **button_config
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        password_btn = tk.Button(
            actions_frame,
            text="🔐 Change Password",
            bg="#fd7e14",
            fg=Colors.WHITE,
            command=self.tab.change_password,
            **button_config
        )
        password_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            actions_frame,
            text="🗑️ Delete User",
            bg=Colors.DANGER,
            fg=Colors.WHITE,
            command=self.tab.delete_user,
            **button_config
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            actions_frame,
            text="🔄 Clear Form",
            bg=Colors.BUTTON_BG,
            fg=Colors.WHITE,
            command=self.tab.clear_form,
            **button_config
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format.
        
        Args:
            email: Email string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength.
        
        Args:
            password: Password string to validate
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_letter and has_digit):
            return False, "Password must contain at least one letter and one number"
        
        return True, "Valid password"
    
    def confirm_action(self, title, message):
        """
        Show confirmation dialog.
        
        Args:
            title: Dialog title
            message: Confirmation message
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        return messagebox.askyesno(title, message)
    
    def show_success(self, message):
        """Show success message."""
        messagebox.showinfo("Success", message)
    
    def show_error(self, message):
        """Show error message."""
        messagebox.showerror("Error", message)
    
    def show_warning(self, message):
        """Show warning message."""
        messagebox.showwarning("Warning", message)
