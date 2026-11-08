"""
Data Tab - Main Controller
Handles roller data management and global limits configuration
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_info
from .global_limits_panel import GlobalLimitsPanel
from .roller_info_panel import RollerInfoPanel
from .roller_data_table import RollerDataTable


class DataTab:
    """Data Management tab for roller configuration."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the data tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.global_limits_panel = None
        self.roller_info_panel = None
        self.roller_data_table = None
        
    def setup(self):
        """Setup the data tab UI."""
        try:
            log_info("data", "Setting up Data tab")
            
            main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
            main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            header_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            title_label = tk.Label(
                header_frame,
                text="Roller Data Management",
                font=("Arial", 20, "bold"),
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG
            )
            title_label.pack()
            
            self.global_limits_panel = GlobalLimitsPanel(main_container, self.app)
            self.global_limits_panel.create()
            
            self.roller_info_panel = RollerInfoPanel(main_container, self.app)
            self.roller_info_panel.create()
            
            self.roller_data_table = RollerDataTable(main_container, self.app)
            self.roller_data_table.create()
            
            self.refresh_data()
            
            log_info("data", "Data tab setup completed")
            
        except Exception as e:
            log_error("data", "Failed to setup Data tab", e)
            raise
    
    def refresh_data(self):
        """Refresh all data from database."""
        if self.global_limits_panel:
            self.global_limits_panel.load_current_limits()
        if self.roller_data_table:
            self.roller_data_table.load_roller_data()
    
    def get_global_limits(self):
        """Get current global limits from panel."""
        if self.global_limits_panel:
            return self.global_limits_panel.get_current_limits()
        return None
