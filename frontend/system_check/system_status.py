"""
System Status Component
Displays system and sensor status information
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class SystemStatus:
    """System status display component."""
    
    def __init__(self, parent, app_instance, system_check_tab):
        """
        Initialize system status.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
            system_check_tab: Reference to SystemCheckTab instance
        """
        self.parent = parent
        self.app = app_instance
        self.system_check_tab = system_check_tab
        
        self.system_status_label = None
        self.system_message_label = None
        self.bf_presence_sensor_label = None
        self.bf_accept_sensor_label = None
        self.od_presence_sensor_label = None
        self.od_accept_sensor_label = None
        
    def create(self):
        """Create the system status UI."""
        status_frame = tk.LabelFrame(
            self.parent,
            text="System Status",
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        inner_frame = tk.Frame(status_frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=1)
        
        self._create_system_status_section(inner_frame)
        
        self._create_sensor_status_section(inner_frame)
    
    def _create_system_status_section(self, parent):
        """Create system status section."""
        status_container = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        status_container.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        title_label = tk.Label(
            status_container,
            text="System Status:",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        self.system_status_label = tk.Label(
            status_container,
            text="STOPPED",
            font=("Arial", 14, "bold"),
            fg="#FF0000",
            bg=Colors.PRIMARY_BG
        )
        self.system_status_label.pack(anchor="w", pady=(0, 5))
        
        warning_frame = tk.Frame(status_container, bg=Colors.PRIMARY_BG)
        warning_frame.pack(anchor="w")
        
        warning_icon = tk.Label(
            warning_frame,
            text="⚠",
            font=("Arial", 12),
            fg="#FFD700",
            bg=Colors.PRIMARY_BG
        )
        warning_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        self.system_message_label = tk.Label(
            warning_frame,
            text="System stopped - No rollers will be processed",
            font=("Arial", 9),
            fg="#FFD700",
            bg=Colors.PRIMARY_BG
        )
        self.system_message_label.pack(side=tk.LEFT)
    
    def _create_sensor_status_section(self, parent):
        """Create sensor status section."""
        sensor_container = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        sensor_container.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        title_label = tk.Label(
            sensor_container,
            text="Sensor Status:",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        bf_presence_frame = tk.Frame(sensor_container, bg=Colors.PRIMARY_BG)
        bf_presence_frame.pack(anchor="w", pady=3)
        
        bf_presence_label = tk.Label(
            bf_presence_frame,
            text="BF Presence:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor="w"
        )
        bf_presence_label.pack(side=tk.LEFT)
        
        self.bf_presence_sensor_label = tk.Label(
            bf_presence_frame,
            text="OFF",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        self.bf_presence_sensor_label.pack(side=tk.LEFT)
        
        bf_accept_frame = tk.Frame(sensor_container, bg=Colors.PRIMARY_BG)
        bf_accept_frame.pack(anchor="w", pady=3)
        
        bf_accept_label = tk.Label(
            bf_accept_frame,
            text="BF Accept/Reject:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor="w"
        )
        bf_accept_label.pack(side=tk.LEFT)
        
        self.bf_accept_sensor_label = tk.Label(
            bf_accept_frame,
            text="OFF",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        self.bf_accept_sensor_label.pack(side=tk.LEFT)
        
        od_presence_frame = tk.Frame(sensor_container, bg=Colors.PRIMARY_BG)
        od_presence_frame.pack(anchor="w", pady=3)
        
        od_presence_label = tk.Label(
            od_presence_frame,
            text="OD Presence:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor="w"
        )
        od_presence_label.pack(side=tk.LEFT)
        
        self.od_presence_sensor_label = tk.Label(
            od_presence_frame,
            text="OFF",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        self.od_presence_sensor_label.pack(side=tk.LEFT)
        
        od_accept_frame = tk.Frame(sensor_container, bg=Colors.PRIMARY_BG)
        od_accept_frame.pack(anchor="w", pady=3)
        
        od_accept_label = tk.Label(
            od_accept_frame,
            text="OD Accept/Reject:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor="w"
        )
        od_accept_label.pack(side=tk.LEFT)
        
        self.od_accept_sensor_label = tk.Label(
            od_accept_frame,
            text="OFF",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        self.od_accept_sensor_label.pack(side=tk.LEFT)
    
    def update_status(self, shared_data, system_running):
        """
        Update status displays from shared data.
        
        Args:
            shared_data: Dictionary containing system status data
            system_running: Boolean indicating if system check is running
        """
        if system_running:
            self.system_status_label.config(text="RUNNING", fg="#00FF00")
            self.system_message_label.config(
                text="✓ System active - Processing rollers",
                fg="#00FF00"
            )
        else:
            self.system_status_label.config(text="STOPPED", fg="#FF0000")
            self.system_message_label.config(
                text="System stopped - No rollers will be processed",
                fg="#FFD700"
            )
        
        bf_presence = shared_data.get('bigface_presence', False)
        
        bf_accept_reject = shared_data.get('bigface', False)
        
        od_presence = shared_data.get('od_presence', False)
        
        od_accept_reject = shared_data.get('od', False)
        
        if bf_presence:
            self.bf_presence_sensor_label.config(text="ON", fg="#00FF00")
        else:
            self.bf_presence_sensor_label.config(text="OFF", fg="#888888")
        
        if bf_accept_reject:
            self.bf_accept_sensor_label.config(text="ON", fg="#00FF00")
        else:
            self.bf_accept_sensor_label.config(text="OFF", fg="#888888")
        
        if od_presence:
            self.od_presence_sensor_label.config(text="ON", fg="#00FF00")
        else:
            self.od_presence_sensor_label.config(text="OFF", fg="#888888")
        
        if od_accept_reject:
            self.od_accept_sensor_label.config(text="ON", fg="#00FF00")
        else:
            self.od_accept_sensor_label.config(text="OFF", fg="#888888")
