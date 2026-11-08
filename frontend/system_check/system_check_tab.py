"""
System Check Tab - Main Controller
Professional interface for BigFace and OD roller inspection control
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info
from .control_settings import ControlSettings
from .system_status import SystemStatus
from .processing_counters import ProcessingCounters
from .system_control import SystemControl
from .plc_controller import PLCController


class SystemCheckTab:
    """System Check tab for PLC control interface."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the system check tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.control_settings = None
        self.system_status = None
        self.processing_counters = None
        self.system_control = None
        self.plc_controller = None
        
        if hasattr(self.app, 'system_check_running'):
            self.system_running = self.app.system_check_running
        else:
            self.system_running = False
            self.app.system_check_running = False
        
        if hasattr(self.app, 'system_check_controls_disabled'):
            self.controls_are_disabled = self.app.system_check_controls_disabled
        else:
            self.controls_are_disabled = False
            self.app.system_check_controls_disabled = False
        
    def setup(self):
        """Setup the system check tab UI."""
        try:
            log_info("system_check", "Setting up System Check tab")
            
            was_running = self.system_running
            
            main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
            main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            title_label = tk.Label(
                main_container,
                text="System Check - PLC Control Interface",
                font=("Arial", 20, "bold"),
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG
            )
            title_label.pack(pady=(0, 2))
            
            subtitle_label = tk.Label(
                main_container,
                text="Professional interface for BigFace and OD roller inspection control",
                font=("Arial", 9),
                fg="#CCCCCC",
                bg=Colors.PRIMARY_BG
            )
            subtitle_label.pack(pady=(0, 10))
            
            controls_disabled = self.controls_are_disabled
            
            self.control_settings = ControlSettings(main_container, self.app)
            self.control_settings.controls_disabled = controls_disabled
            self.control_settings.create()
            
            if self.plc_controller is None:
                self.plc_controller = PLCController(self.app, self.control_settings)
            else:
                self.plc_controller.control_settings = self.control_settings
            
            self.system_status = SystemStatus(main_container, self.app, self)
            self.system_status.create()
            
            self.processing_counters = ProcessingCounters(main_container, self.app)
            self.processing_counters.create()
            
            self.system_control = SystemControl(main_container, self.app, self)
            self.system_control.create()
            
            if was_running:
                self.system_control.enable_stop()
                self._block_navigation_buttons()
                if hasattr(self.app, 'protocol'):
                    self.app.protocol("WM_DELETE_WINDOW", self.system_control._block_closing)
            
            self._monitor_updates()
            
            log_info("system_check", "System Check tab setup completed successfully")
        except Exception as e:
            log_error("system_check", "Failed to setup System Check tab", e)
            raise
    
    def _monitor_updates(self):
        """Monitor shared_data for real-time updates."""
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            if self.system_status:
                self.system_status.update_status(self.app.shared_data, self.system_running)
            
            if self.processing_counters:
                self.processing_counters.update_counters(self.app.shared_data)
        
        try:
            self.parent.after(100, self._monitor_updates)
        except:
            pass
    
    def start_system(self):
        """Start the system check control."""
        if self.system_running:
            print("⚠ System Check: Already running")
            return False
        
        if not self._check_plc_connection():
            return False
        
        if self.plc_controller.start_monitoring():
            self.system_running = True
            self.app.system_check_running = True
            
            self._block_navigation_buttons()
            
            self._block_logout_button()
            
            if self.control_settings:
                self.control_settings.disable_controls()
                self.controls_are_disabled = True
                self.app.system_check_controls_disabled = True
            
            if self.system_control:
                self.system_control.enable_stop()
            
            if hasattr(self.app, '_monitor_system_error'):
                self.app._monitor_system_error()
            
            return True
        else:
            print("❌ System Check: Failed to start system")
            return False
    
    def stop_system(self):
        """Stop the system check control."""
        if not self.system_running:
            print("⚠ System Check: Not running")
            return
        
        self.plc_controller.stop_monitoring()
        self.system_running = False
        self.app.system_check_running = False
        
        self._unblock_navigation_buttons()
        
        self._unblock_logout_button()
        
        if self.control_settings:
            self.control_settings.enable_controls()
            self.controls_are_disabled = False
            self.app.system_check_controls_disabled = False
        
        if self.system_control:
            self.system_control.enable_start()
        
    
    def reset_counters(self):
        """Reset all processing counters."""
        if self.plc_controller:
            self.plc_controller.reset_counters()
    
    def _block_navigation_buttons(self):
        """Block Inference and Settings navigation buttons with red color."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            if 'inference' in navbar.buttons:
                navbar.buttons['inference'].button.config(
                    state=tk.DISABLED,
                    bg="#DC3545",
                    disabledforeground="#FFFFFF"
                )
            
            if 'settings' in navbar.buttons:
                navbar.buttons['settings'].button.config(
                    state=tk.DISABLED,
                    bg="#DC3545",
                    disabledforeground="#FFFFFF"
                )
    
    def _unblock_navigation_buttons(self):
        """Unblock Inference and Settings navigation buttons."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            if 'inference' in navbar.buttons:
                nav_button = navbar.buttons['inference']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
            
            if 'settings' in navbar.buttons:
                nav_button = navbar.buttons['settings']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
    
    def _block_logout_button(self):
        """Block the logout button during system check with grey color."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.DISABLED,
                bg="#6c757d",
                fg="#FFFFFF"
            )
    
    def _unblock_logout_button(self):
        """Unblock the logout button after system check with red color."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            from ..utils.styles import Colors
            self.app.logout_button.config(
                state=tk.NORMAL,
                bg=Colors.DANGER,
                fg="#FFFFFF"
            )
    
    def _check_plc_connection(self):
        """
        Check PLC connection before starting system check.
        
        Returns:
            bool: True if PLC is connected, False otherwise
        """
        try:
            import snap7
            from tkinter import messagebox
            from ..utils.config import AppConfig
            
            plc = snap7.client.Client()
            plc.connect(AppConfig.PLC_IP, AppConfig.PLC_RACK, AppConfig.PLC_SLOT)
            
            if plc.get_connected():
                plc.disconnect()
                return True
            else:
                messagebox.showerror(
                    "PLC Not Connected",
                    f"⚠️ Cannot connect to PLC at {AppConfig.PLC_IP}\n\n"
                    "Please check:\n"
                    "• PLC is powered on\n"
                    "• Network cable is connected\n"
                    "• IP address is correct\n\n"
                    "System Check cannot start without PLC connection."
                )
                return False
        
        except Exception as e:
            from tkinter import messagebox
            from ..utils.config import AppConfig
            messagebox.showerror(
                "PLC Connection Failed",
                f"⚠️ PLC Connection Error\n\n"
                f"IP: {AppConfig.PLC_IP}\n"
                f"Error: {str(e)}\n\n"
                "Please check:\n"
                "• PLC is powered on\n"
                "• Network cable is connected\n"
                "• Firewall settings\n\n"
                "System Check cannot start without PLC connection."
            )
            return False
