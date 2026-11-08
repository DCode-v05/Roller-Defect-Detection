"""
Preview Control Panel Component for Settings Tab
Contains Start/Stop Preview buttons
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class PreviewControlPanel:
    """Control panel for camera preview operations in settings."""
    
    def __init__(self, parent, settings_tab_instance):
        """
        Initialize the preview control panel.
        
        Args:
            parent: Parent frame
            settings_tab_instance: Reference to settings tab instance
        """
        self.parent = parent
        self.settings_tab = settings_tab_instance
        self.start_button = None
        self.stop_button = None
        self.capture_bf_button = None
        self.capture_od_button = None
        self.control_frame = None
        
    def setup(self):
        """Setup the preview control panel UI."""
        self.control_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = tk.Button(
            self.control_frame,
            text="▶ Start Preview",
            font=Fonts.TEXT_BOLD,
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            disabledforeground=Colors.WHITE,
            width=20,
            height=2,
            command=self._on_start_preview
        )
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.stop_button = tk.Button(
            self.control_frame,
            text="⏹ Stop Preview",
            font=Fonts.TEXT_BOLD,
            bg="#6c757d",
            fg=Colors.WHITE,
            disabledforeground=Colors.WHITE,
            width=20,
            height=2,
            command=self._on_stop_preview,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.capture_bf_button = tk.Button(
            self.control_frame,
            text="📸 Capture BF",
            font=Fonts.TEXT_BOLD,
            bg="#FFA500",
            fg=Colors.WHITE,
            width=15,
            height=2,
            command=self._on_capture_bf
        )
        
        self.capture_od_button = tk.Button(
            self.control_frame,
            text="📸 Capture OD",
            font=Fonts.TEXT_BOLD,
            bg="#FFA500",
            fg=Colors.WHITE,
            width=15,
            height=2,
            command=self._on_capture_od
        )
        
        return self.control_frame
    
    def _on_start_preview(self):
        """Handle start preview button click."""
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Confirm Start Preview",
            "Are you sure you want to start the camera preview?\n\n"
            "This will load models and start camera feeds for testing thresholds.",
            icon='question'
        )
        
        if not confirm:
            return
        
        success = self.settings_tab.start_preview()
        
        if success:
            self.enable_stop()
    
    def _on_stop_preview(self):
        """Handle stop preview button click."""
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Confirm Stop Preview",
            "Are you sure you want to stop the camera preview?\n\n"
            "This will unload models and stop camera feeds.",
            icon='question'
        )
        
        if not confirm:
            return
        
        self.settings_tab.stop_preview()
        
        self.enable_start()
    
    def _on_capture_bf(self):
        """Handle capture BF button click."""
        self.settings_tab.capture_bf_frame()
    
    def _on_capture_od(self):
        """Handle capture OD button click."""
        self.settings_tab.capture_od_frame()
    
    def enable_start(self):
        """Enable the start button and disable stop button."""
        if self.start_button:
            self.start_button.config(state=tk.NORMAL, bg=Colors.SUCCESS)
        if self.stop_button:
            self.stop_button.config(state=tk.DISABLED, bg="#6c757d")
        
        if self.capture_bf_button:
            self.capture_bf_button.pack_forget()
        if self.capture_od_button:
            self.capture_od_button.pack_forget()
    
    def enable_stop(self):
        """Enable the stop button and disable start button."""
        if self.start_button:
            self.start_button.config(state=tk.DISABLED, bg="#6c757d")
        if self.stop_button:
            self.stop_button.config(state=tk.NORMAL, bg=Colors.DANGER)
        
        if self.capture_bf_button:
            self.capture_bf_button.pack(side=tk.LEFT, padx=10, pady=5)
        if self.capture_od_button:
            self.capture_od_button.pack(side=tk.LEFT, padx=10, pady=5)
