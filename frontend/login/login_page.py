"""
Login Page UI Component - Main Controller
Orchestrates all login page components
"""

import tkinter as tk
from .window_config import WindowConfig
from .login_form import LoginForm
from .login_header import LoginHeader
from .role_selector import RoleSelector
from .input_fields import InputFields
from .signin_button import SignInButton
from .auth_handler import AuthHandler


class LoginPage:
    """Main login page controller that orchestrates all components."""
    
    def __init__(self, parent, on_login_success):
        """
        Initialize the login page.
        
        Args:
            parent: Parent Tk window
            on_login_success: Callback function when login is successful
                             Should accept (email, role) as parameters
        """
        self.parent = parent
        self.on_login_success = on_login_success
        
        self.login_form = None
        self.role_selector = None
        self.input_fields = None
        self.signin_button = None
        
        WindowConfig.configure(self.parent)
        
    def show(self):
        """Display the login page."""
        self._clear_widgets()
        
        self._build_login_form()
        
        self.parent.bind("<Return>", lambda event: self._on_enter_key_press())
        
    def _clear_widgets(self):
        """Clear any existing widgets from parent."""
        for widget in self.parent.winfo_children():
            widget.destroy()
    
    def _build_login_form(self):
        """Build the complete login form with all components."""
        self.login_form = LoginForm(self.parent)
        container = self.login_form.create()
        
        LoginHeader.create(container)
        
        self.role_selector = RoleSelector(container)
        self.role_selector.create()
        
        self.input_fields = InputFields(container)
        self.input_fields.create()
        
        self.signin_button = SignInButton(container, self._authenticate)
        self.signin_button.create()
        
    def _on_enter_key_press(self):
        """Handle Enter key press with visual button feedback."""
        if self.signin_button and self.signin_button.button:
            try:
                if self.signin_button.button.winfo_exists():
                    self.signin_button.trigger_press_animation(callback=self._authenticate)
                else:
                    self._authenticate()
            except tk.TclError:
                self._authenticate()
        else:
            self._authenticate()
    
    def _authenticate(self):
        """Handle authentication logic."""
        if not self.input_fields or not hasattr(self.input_fields, 'email_entry'):
            return
        
        try:
            if not self.input_fields.email_entry.winfo_exists():
                return
        except (tk.TclError, AttributeError):
            return
        
        email, password = self.input_fields.get_credentials()
        role = self.role_selector.role_var.get()
        
        success, error_message = AuthHandler.authenticate(email, password, role)
        
        if success:
            try:
                self.parent.unbind("<Return>")
            except:
                pass
            
            self._cleanup()
            self.on_login_success(email, role)
        else:
            if self.signin_button:
                self.signin_button.reset_to_normal()
            AuthHandler.show_error(error_message)
    
    def _cleanup(self):
        """Clean up login form resources."""
        if self.login_form:
            self.login_form.destroy()
            self.login_form = None
    
    def hide(self):
        """Hide the login page."""
        self._cleanup()
