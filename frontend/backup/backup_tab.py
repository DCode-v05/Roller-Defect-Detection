"""
Backup Tab - Main Controller
Image Backup and Database Backup Management
Admin and Super Admin only
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info
from .image_backup import ImageBackupManager
from .database_backup import DatabaseBackupManager


class BackupTab:
    """Backup tab for image and database backup operations."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the backup tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.image_manager = None
        self.database_manager = None
        
    def setup(self):
        """Setup the backup tab UI - optimized to fit without scrolling."""
        try:
            log_info("backup", "Setting up Backup tab")
            
            main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
            main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            title_label = tk.Label(
                main_container,
                text="Backup & Restore Management",
                font=Fonts.LARGE,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG
            )
            title_label.pack(pady=(5, 2))
            
            subtitle_label = tk.Label(
                main_container,
                text="Database Backup & Inference Images Backup",
                font=Fonts.SMALL,
                fg="#AAAAAA",
                bg=Colors.PRIMARY_BG
            )
            subtitle_label.pack(pady=(0, 8))
            
            sections_container = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
            sections_container.pack(fill=tk.X, pady=5)
            
            db_section_frame = tk.LabelFrame(
                sections_container,
                text="💾 Database Backup & Restore",
                font=Fonts.HEADER,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG,
                bd=2,
                relief=tk.RIDGE,
                padx=15,
                pady=10
            )
            db_section_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5), anchor=tk.N)
            
            self.database_manager = DatabaseBackupManager(self.parent)
            self.database_manager.create_ui(db_section_frame)
            
            image_section_frame = tk.LabelFrame(
                sections_container,
                text="🖼️ Inference Images Backup",
                font=Fonts.HEADER,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG,
                bd=2,
                relief=tk.RIDGE,
                padx=15,
                pady=10
            )
            image_section_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5), anchor=tk.N)
            
            self.image_manager = ImageBackupManager(self.parent)
            self.image_manager.create_ui(image_section_frame)
            
            log_info("backup", "Backup tab setup completed successfully")
        except Exception as e:
            log_error("backup", "Failed to setup Backup tab", e)
            raise
