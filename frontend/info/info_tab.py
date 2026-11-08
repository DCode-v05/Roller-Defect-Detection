"""
Info Tab - Main Controller
Manages application settings, system information, and user manual
"""

import tkinter as tk
import tkinter.ttk as ttk
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info
from .title_management import TitleManagement
from .settings_history import SettingsHistory
from .system_information import SystemInformation
from .database_config import DatabaseConfig
from .user_manual import UserManual


class InfoTab:
    """Info tab for application settings and system information."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the info tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.title_management = None
        self.settings_history = None
        self.system_information = None
        self.database_config = None
        self.user_manual = None
        
        self.canvas = None
        self.scrollable_frame = None
        self._mousewheel_bound = False
    
    def setup(self):
        """Setup the info tab UI with scrolling support."""
        try:
            log_info("info", "Setting up Info tab")
            
            if self._mousewheel_bound:
                try:
                    if hasattr(self, 'canvas') and self.canvas:
                        self.canvas.unbind_all("<MouseWheel>")
                    self._mousewheel_bound = False
                except:
                    pass
            
            main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
            main_container.pack(fill=tk.BOTH, expand=True)
            
            title_label = tk.Label(
                main_container,
                text="Application Settings",
                font=Fonts.TITLE,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG
            )
            title_label.pack(pady=(10, 5))
            
            subtitle_label = tk.Label(
                main_container,
                text="Configure application preferences and system settings",
                font=Fonts.TEXT,
                fg="#CCCCCC",
                bg=Colors.PRIMARY_BG
            )
            subtitle_label.pack(pady=(0, 10))
            
            self.canvas = tk.Canvas(main_container, bg=Colors.PRIMARY_BG, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
            self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.PRIMARY_BG)
            
            self._scroll_update_id = None
            self._last_scroll_update = 0
            
            def _update_scroll_region(event=None):
                if self._scroll_update_id:
                    self.canvas.after_cancel(self._scroll_update_id)
                
                import time
                current_time = time.time()
                if current_time - self._last_scroll_update < 0.2:
                    return
                
                def _do_update():
                    try:
                        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                        self._last_scroll_update = time.time()
                    except:
                        pass
                
                self._scroll_update_id = self.canvas.after(200, _do_update)
            
            self.scrollable_frame.bind("<Configure>", _update_scroll_region)
            
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
            self.canvas.configure(yscrollcommand=scrollbar.set)
            
            self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
            scrollbar.pack(side="right", fill="y")
            
            def _on_canvas_configure(event):
                self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)
            
            self.canvas.bind("<Configure>", _on_canvas_configure)
            
            def _on_mousewheel(event):
                if not self.canvas or not self.canvas.winfo_exists():
                    return
                
                try:
                    self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
                except tk.TclError:
                    pass
            
            def _bind_mousewheel(event=None):
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
                self._mousewheel_bound = True
            
            def _unbind_mousewheel(event=None):
                if self._mousewheel_bound:
                    try:
                        self.canvas.unbind_all("<MouseWheel>")
                        self._mousewheel_bound = False
                    except:
                        pass
            
            self.canvas.bind("<Enter>", _bind_mousewheel)
            self.canvas.bind("<Leave>", _unbind_mousewheel)
            
            _bind_mousewheel()
            
            loading_label = tk.Label(
                self.scrollable_frame,
                text="⏳ Loading components...",
                font=Fonts.SUBTITLE,
                fg="#FFD700",
                bg=Colors.PRIMARY_BG,
                pady=50
            )
            loading_label.pack()
            
            self.parent.after(50, lambda: self._load_components(loading_label))
            
            log_info("info", "Info tab setup initiated (components loading asynchronously)")
        except Exception as e:
            log_error("info", "Failed to setup Info tab", e)
            raise
    
    def _load_components(self, loading_label):
        """Load all components asynchronously."""
        loading_label.destroy()
        
        self.title_management = TitleManagement(self.scrollable_frame, self.app)
        self.title_management.create()
        
        self.parent.after(10, self._load_settings_history)
    
    def _load_settings_history(self):
        """Load settings history component."""
        self.settings_history = SettingsHistory(self.scrollable_frame, self.app)
        self.settings_history.create()
        
        self.parent.after(10, self._load_system_info)
    
    def _load_system_info(self):
        """Load system information component."""
        self.system_information = SystemInformation(self.scrollable_frame, self.app)
        self.system_information.create()
        
        self.parent.after(10, self._load_database_config)
    
    def _load_database_config(self):
        """Load database config component."""
        user_role = getattr(self.app, 'current_role', 'Operator')
        if user_role == 'Super Admin':
            self.database_config = DatabaseConfig(self.scrollable_frame, self.app)
            self.database_config.create()
        
        self.parent.after(10, self._load_user_manual)
    
    def _load_user_manual(self):
        """Load user manual component."""
        self.user_manual = UserManual(self.scrollable_frame, self.app)
        self.user_manual.create()
        
        def _final_update():
            try:
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except:
                pass
        self.canvas.after(100, _final_update)
    
    def cleanup(self):
        """Cleanup method called when tab is destroyed."""
        if self._mousewheel_bound:
            try:
                self.canvas.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
