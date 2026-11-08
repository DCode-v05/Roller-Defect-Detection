"""
Navigation Bar Manager
Main controller for the navigation bar system
"""

import tkinter as tk
from ..utils.styles import Colors
from ..utils.permissions import Permissions
from .nav_button import NavButton
from .nav_config import NavConfig


class NavBarManager:
    """Manages the navigation bar and its buttons."""
    
    def __init__(self, parent, on_nav_change, app_instance=None):
        """
        Initialize the navigation bar manager.
        
        Args:
            parent: Parent frame
            on_nav_change: Callback function when navigation changes
                          Should accept button_id as parameter
            app_instance: Reference to main app instance for role checking
        """
        self.parent = parent
        self.on_nav_change = on_nav_change
        self.app = app_instance
        self.navbar_frame = None
        self.buttons = {}
        self.active_button_id = None
        
    def create(self):
        """Create the navigation bar with role-based access control."""
        self.navbar_frame = tk.Frame(
            self.parent,
            bg=Colors.PRIMARY_BG,
            height=NavConfig.NAVBAR_HEIGHT
        )
        self.navbar_frame.pack(
            fill=tk.X,
            padx=NavConfig.NAVBAR_PADDING_X,
            pady=NavConfig.NAVBAR_PADDING_Y
        )
        
        buttons_container = tk.Frame(
            self.navbar_frame,
            bg=Colors.PRIMARY_BG
        )
        buttons_container.pack(anchor=tk.W, padx=5)
        
        user_role = getattr(self.app, 'current_role', 'Operator') if self.app else 'Operator'
        
        for button_id, button_text, _ in NavConfig.get_button_configs():
            if self._can_access_tab(button_id, user_role):
                nav_button = NavButton(
                    buttons_container,
                    button_text,
                    self._handle_nav_click,
                    button_id
                )
                nav_button.create()
                nav_button.pack(side=tk.LEFT, padx=NavConfig.BUTTON_GAP)
                
                self.buttons[button_id] = nav_button
        
        return self.navbar_frame
    
    def _can_access_tab(self, tab_id, user_role):
        """
        Check if user can access a specific tab.
        
        Args:
            tab_id: Tab identifier
            user_role: User's role
            
        Returns:
            bool: True if user can access, False otherwise
        """
        if tab_id == "model_management":
            return Permissions.can_access_model_management_tab(user_role)
        
        elif tab_id == "user_management":
            return Permissions.can_access_user_management_tab(user_role)
        
        elif tab_id == "system_check":
            return Permissions.can_access_system_check_tab(user_role)
        
        elif tab_id == "backup":
            return Permissions.can_access_backup_tab(user_role)
        
        else:
            return True
    
    def _handle_nav_click(self, button_id):
        """
        Handle navigation button click.
        
        Args:
            button_id: ID of the clicked button
        """
        self.set_active_button(button_id)
        
        if self.on_nav_change:
            self.on_nav_change(button_id)
    
    def set_active_button(self, button_id):
        """
        Set the active button and update visual states.
        
        Args:
            button_id: ID of the button to set as active
        """
        if self.active_button_id and self.active_button_id in self.buttons:
            self.buttons[self.active_button_id].set_active(False)
        
        if button_id in self.buttons:
            self.buttons[button_id].set_active(True)
            self.active_button_id = button_id
    
    def get_active_button_id(self):
        """Get the currently active button ID."""
        return self.active_button_id
    
    def enable_button(self, button_id):
        """Enable a specific button."""
        if button_id in self.buttons:
            self.buttons[button_id].button.config(state=tk.NORMAL)
    
    def disable_button(self, button_id):
        """Disable a specific button."""
        if button_id in self.buttons:
            self.buttons[button_id].button.config(state=tk.DISABLED)
