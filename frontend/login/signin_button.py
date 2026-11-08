"""
Sign In Button Module
Button component with hover effects and press animations
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class SignInButton:
    """Sign-in button with proper styling, hover effects, and press animations."""
    
    def __init__(self, parent, command):
        """
        Initialize the sign-in button.
        
        Args:
            parent: Parent frame to contain the button
            command: Callback function when button is clicked
        """
        self.parent = parent
        self.command = command
        self.button = None
        self._is_animating = False
        
    def create(self):
        """
        Create the sign-in button with proper styling.
        
        Returns:
            button: The created button widget
        """
        self.button = tk.Button(
            self.parent, 
            text="Sign In", 
            font=Fonts.TEXT_BOLD,
            bg=Colors.PRIMARY_BLUE, 
            fg=Colors.WHITE, 
            width=25, 
            height=2,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            command=self._on_button_click,
            activebackground=Colors.PRIMARY_BLUE,
            activeforeground=Colors.WHITE
        )
        self.button.pack(pady=20)
        
        self._bind_hover_effects()
        
        return self.button
    
    def _bind_hover_effects(self):
        """Bind hover effects to the sign-in button."""
        def on_enter(event):
            """Handle mouse enter event."""
            if not self._is_animating and self.button and self.button.winfo_exists():
                try:
                    self.button.config(bg="#0056b3")
                except tk.TclError:
                    pass
            
        def on_leave(event):
            """Handle mouse leave event."""
            if not self._is_animating and self.button and self.button.winfo_exists():
                try:
                    self.button.config(bg=Colors.PRIMARY_BLUE)
                except tk.TclError:
                    pass
            
        self.button.bind("<Enter>", on_enter)
        self.button.bind("<Leave>", on_leave)
    
    def _on_button_click(self):
        """Handle button click with visual feedback animation."""
        if self._is_animating:
            return
        
        self._animate_press(callback=self.command)
    
    def _animate_press(self, callback=None):
        """
        Animate button press with color change.
        
        Args:
            callback: Optional callback to execute after animation
        """
        if not self.button or not self.button.winfo_exists():
            if callback:
                callback()
            return
        
        self._is_animating = True
        
        try:
            self.button.config(bg="#FFFFFF", relief=tk.SUNKEN, text="Signing In...", fg="#000000")
            
            self.button.after(150, lambda: self._reset_button_state(callback))
        except tk.TclError:
            self._is_animating = False
            if callback:
                callback()
    
    def _reset_button_state(self, callback=None):
        """
        Reset button to normal state after animation.
        
        Args:
            callback: Optional callback to execute after reset
        """
        if not self.button or not self.button.winfo_exists():
            self._is_animating = False
            if callback:
                callback()
            return
        
        try:
            self.button.config(
                bg=Colors.PRIMARY_BLUE, 
                relief=tk.FLAT,
                text="Sign In",
                fg=Colors.WHITE
            )
            self._is_animating = False
            
            if callback:
                callback()
        except tk.TclError:
            self._is_animating = False
            if callback:
                callback()
    
    def reset_to_normal(self):
        """Force reset button to normal state (for failed authentication)."""
        if not self.button or not self.button.winfo_exists():
            self._is_animating = False
            return
        
        try:
            self.button.config(
                bg=Colors.PRIMARY_BLUE,
                relief=tk.FLAT,
                text="Sign In",
                fg=Colors.WHITE
            )
            self._is_animating = False
        except tk.TclError:
            self._is_animating = False
    
    def trigger_press_animation(self, callback=None):
        """
        Trigger the press animation programmatically (for Enter key).
        
        Args:
            callback: Optional callback to execute after animation
        """
        if not self.button or not self.button.winfo_exists():
            if callback:
                callback()
            return
        
        if self._is_animating:
            return
        
        self._animate_press(callback=callback)
