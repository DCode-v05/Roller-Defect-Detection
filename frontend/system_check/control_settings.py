"""
Control Settings Component
BigFace and OD pattern selection controls
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class ControlSettings:
    """Control settings for BigFace and OD inspection patterns."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize control settings.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.bf_pattern = "ACCEPT ALL"
        self.od_pattern = "ACCEPT ALL"
        
        self.bf_radio_buttons = []
        self.od_radio_buttons = []
        
        self.controls_disabled = False
        
    def create(self):
        """Create the control settings UI."""
        self.bf_radio_buttons = []
        self.od_radio_buttons = []
        
        settings_frame = tk.LabelFrame(
            self.parent,
            text="Control Settings",
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        inner_frame = tk.Frame(settings_frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=1)
        
        self._create_bf_control(inner_frame)
        
        self._create_od_control(inner_frame)
        
        if self.controls_disabled:
            self._apply_disabled_state()
    
    def _create_bf_control(self, parent):
        """Create BigFace control section."""
        bf_frame = tk.LabelFrame(
            parent,
            text="BigFace Control",
            font=("Arial", 10, "bold"),
            fg="#00FFFF",
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        bf_frame.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")
        
        bf_inner = tk.Frame(bf_frame, bg=Colors.PRIMARY_BG)
        bf_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        label = tk.Label(
            bf_inner,
            text="Select Pattern:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        label.pack(anchor="w", pady=(0, 5))
        
        self.bf_pattern_var = tk.StringVar(value="ACCEPT ALL")
        
        patterns = [
            ("Accept All", "ACCEPT ALL"),
            ("Reject All", "REJECT ALL"),
            ("Alternate (1-0-1-0)", "ALTERNATE")
        ]
        
        for text, value in patterns:
            rb = tk.Radiobutton(
                bf_inner,
                text=text,
                variable=self.bf_pattern_var,
                value=value,
                font=("Arial", 9),
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG,
                selectcolor=Colors.SECONDARY_BG,
                activebackground=Colors.PRIMARY_BG,
                activeforeground=Colors.WHITE,
                command=lambda v=value: self._update_bf_pattern(v)
            )
            rb.pack(anchor="w", pady=2)
            self.bf_radio_buttons.append(rb)
        
        self.bf_status_label = tk.Label(
            bf_inner,
            text=f"Current: {self.bf_pattern}",
            font=("Arial", 9, "bold"),
            fg="#00FF00",
            bg=Colors.PRIMARY_BG
        )
        self.bf_status_label.pack(anchor="w", pady=(8, 0))
    
    def _create_od_control(self, parent):
        """Create OD control section."""
        od_frame = tk.LabelFrame(
            parent,
            text="OD Control",
            font=("Arial", 10, "bold"),
            fg="#00FFFF",
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        od_frame.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")
        
        od_inner = tk.Frame(od_frame, bg=Colors.PRIMARY_BG)
        od_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        label = tk.Label(
            od_inner,
            text="Select Pattern:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        label.pack(anchor="w", pady=(0, 5))
        
        self.od_pattern_var = tk.StringVar(value="ACCEPT ALL")
        
        patterns = [
            ("Accept All", "ACCEPT ALL"),
            ("Reject All", "REJECT ALL"),
            ("Alternate (1-0-1-0)", "ALTERNATE")
        ]
        
        for text, value in patterns:
            rb = tk.Radiobutton(
                od_inner,
                text=text,
                variable=self.od_pattern_var,
                value=value,
                font=("Arial", 9),
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG,
                selectcolor=Colors.SECONDARY_BG,
                activebackground=Colors.PRIMARY_BG,
                activeforeground=Colors.WHITE,
                command=lambda v=value: self._update_od_pattern(v)
            )
            rb.pack(anchor="w", pady=2)
            self.od_radio_buttons.append(rb)
        
        self.od_status_label = tk.Label(
            od_inner,
            text=f"Current: {self.od_pattern}",
            font=("Arial", 9, "bold"),
            fg="#00FF00",
            bg=Colors.PRIMARY_BG
        )
        self.od_status_label.pack(anchor="w", pady=(8, 0))
    
    def _update_bf_pattern(self, pattern):
        """Update BigFace pattern."""
        self.bf_pattern = pattern
        self.bf_status_label.config(text=f"Current: {pattern}")
        print(f"BigFace pattern set to: {pattern}")
    
    def _update_od_pattern(self, pattern):
        """Update OD pattern."""
        self.od_pattern = pattern
        self.od_status_label.config(text=f"Current: {pattern}")
        print(f"OD pattern set to: {pattern}")
    
    def disable_controls(self):
        """Disable all pattern selection controls."""
        self.controls_disabled = True
        self._apply_disabled_state()
    
    def _apply_disabled_state(self):
        """Apply disabled state to all radio buttons."""
        for rb in self.bf_radio_buttons:
            rb.config(state=tk.DISABLED)
        
        for rb in self.od_radio_buttons:
            rb.config(state=tk.DISABLED)
            
    def enable_controls(self):
        """Enable all pattern selection controls."""
        self.controls_disabled = False
        
        for rb in self.bf_radio_buttons:
            rb.config(state=tk.NORMAL)
        
        for rb in self.od_radio_buttons:
            rb.config(state=tk.NORMAL)
        