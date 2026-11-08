"""
State Manager for Inspection UI
Manages button and tab states during inspection start/stop
"""

import tkinter as tk
from ..utils.styles import Colors


class InspectionStateManager:
    """Manages UI state changes during inspection."""
    
    def __init__(self, app_instance):
        """
        Initialize the state manager.
        
        Args:
            app_instance: Reference to main WelVisionApp instance
        """
        self.app = app_instance
        self.original_close_handler = None
        
    def on_inspection_start(self, control_panel):
        """
        Handle UI state changes when inspection starts.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        self._apply_control_panel_inspection_state(control_panel)
        
        self._lock_roller_selection()
        
        self._disable_logout_button()
        
        self._disable_window_close()
        
        self._disable_other_tabs()
    
    def restore_control_panel_state(self, control_panel):
        """
        Restore control panel button states when returning to inference tab during inspection.
        Does not modify tabs, logout button, or window close state.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        self._apply_control_panel_inspection_state(control_panel)
    
    def _apply_control_panel_inspection_state(self, control_panel):
        """
        Apply inspection state to control panel buttons.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        if control_panel.start_button:
            control_panel.start_button.config(
                state=tk.DISABLED,
                bg="#6c757d",
                fg=Colors.WHITE
            )
        
        if control_panel.stop_button:
            control_panel.stop_button.config(
                state=tk.NORMAL,
                bg=Colors.DANGER,
                fg=Colors.WHITE
            )
        
        if control_panel.reset_button:
            control_panel.reset_button.config(
                state=tk.DISABLED,
                bg="#6c757d",
                fg=Colors.WHITE
            )
    
        if hasattr(control_panel, 'allow_images_checkbox') and control_panel.allow_images_checkbox:
            control_panel.allow_images_checkbox.config(state=tk.DISABLED)
    
    def on_inspection_stop(self, control_panel):
        """
        Handle UI state changes when inspection stops.
        
        Args:
            control_panel: Reference to ControlPanel instance
        """
        if control_panel.start_button:
            control_panel.start_button.config(
                state=tk.NORMAL,
                bg=Colors.SUCCESS,
                fg=Colors.WHITE
            )
        
        if control_panel.stop_button:
            control_panel.stop_button.config(
                state=tk.DISABLED,
                bg="#6c757d",
                fg=Colors.WHITE
            )
        
        
        if hasattr(control_panel, 'allow_images_checkbox') and control_panel.allow_images_checkbox:
            control_panel.allow_images_checkbox.config(state=tk.NORMAL)
        
        self._unlock_roller_selection()
        
        self._enable_logout_button()
        
        self._enable_window_close()
        
        self._enable_all_tabs()
    
    def _disable_logout_button(self):
        """Disable the logout button with grey color and white text."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.DISABLED,
                bg="#6c757d",
                fg=Colors.WHITE
            )
    
    def _enable_logout_button(self):
        """Enable the logout button with red color and white text."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.NORMAL,
                bg=Colors.DANGER,
                fg=Colors.WHITE
            )
    
    def _disable_window_close(self):
        """Disable the window close button (top right X)."""
        self.original_close_handler = self.app.protocol("WM_DELETE_WINDOW")
        
        self.app.protocol("WM_DELETE_WINDOW", self._on_disabled_close)
    
    def _enable_window_close(self):
        """Enable the window close button (top right X)."""
        if self.original_close_handler:
            self.app.protocol("WM_DELETE_WINDOW", self.original_close_handler)
        elif hasattr(self.app, 'on_closing'):
            self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
        else:
            self.app.protocol("WM_DELETE_WINDOW", self.app.destroy)
    
    def _on_disabled_close(self):
        """Show warning when trying to close during inspection."""
        from tkinter import messagebox
        messagebox.showwarning(
            "Inspection Running",
            "⚠️ Please stop the inspection before closing the application."
        )
    
    def _disable_other_tabs(self):
        """Disable all navigation tabs except Inference and Diagnosis with red color and white text."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            for button_id, nav_button in navbar.buttons.items():
                if button_id not in ["inference", "diagnosis"]:
                    nav_button.button.config(
                        state=tk.DISABLED,
                        bg=Colors.DANGER,
                        fg=Colors.WHITE,
                        disabledforeground=Colors.WHITE
                    )
                    
                    nav_button.button.unbind("<Enter>")
                    nav_button.button.unbind("<Leave>")
    
    def _enable_all_tabs(self):
        """Enable all navigation tabs with normal colors and restore hover events."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            for button_id, nav_button in navbar.buttons.items():
                nav_button.button.config(state=tk.NORMAL)
                
                if nav_button.is_active:
                    nav_button.button.config(bg=nav_button.active_bg)
                else:
                    nav_button.button.config(bg=nav_button.inactive_bg)
                
                nav_button.button.bind("<Enter>", nav_button._on_hover)
                nav_button.button.bind("<Leave>", nav_button._on_leave)
    
    def _lock_roller_selection(self):
        """Lock roller type dropdown during inspection."""
        if hasattr(self.app, 'inference_tab') and self.app.inference_tab:
            if hasattr(self.app.inference_tab, 'status_panel') and self.app.inference_tab.status_panel:
                self.app.inference_tab.status_panel.lock_roller_selection()
    
    def _unlock_roller_selection(self):
        """Unlock roller type dropdown after inspection stops."""
        if hasattr(self.app, 'inference_tab') and self.app.inference_tab:
            if hasattr(self.app.inference_tab, 'status_panel') and self.app.inference_tab.status_panel:
                self.app.inference_tab.status_panel.unlock_roller_selection()
