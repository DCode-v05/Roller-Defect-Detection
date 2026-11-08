"""
Database Backup Manager
Handles MySQL database backup and restore operations
"""

import tkinter as tk
import tkinter.messagebox as messagebox
import os
import subprocess
from datetime import datetime
from pathlib import Path
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig
from ..utils.debug_logger import log_error, log_warning, log_info
from .database_operations import DatabaseOperations
from .storage_checker import StorageChecker


class DatabaseBackupManager:
    """Manager for database backup and restore operations."""
    
    def __init__(self, parent):
        """
        Initialize the database backup manager.
        
        Args:
            parent: Parent frame for UI components
        """
        self.parent = parent
        self.db_ops = DatabaseOperations()
        
        self.backup_button = None
        self.restore_button = None
        self.status_label = None
        
    def create_ui(self, container_frame):
        """
        Create the database backup UI inside the provided container.
        
        Args:
            container_frame: Container frame to hold the UI elements
        """
        desc_label = tk.Label(
            container_frame,
            text="Backup entire MySQL database to SQL file or restore from backup",
            font=Fonts.SMALL,
            fg="#CCCCCC",
            bg=Colors.PRIMARY_BG,
            justify=tk.LEFT,
            wraplength=500
        )
        desc_label.pack(anchor=tk.W, pady=(2, 8))
        
        buttons_frame = tk.Frame(container_frame, bg=Colors.PRIMARY_BG)
        buttons_frame.pack(pady=5)
        
        self.backup_button = tk.Button(
            buttons_frame,
            text="💾 Backup Database",
            font=Fonts.TEXT_BOLD,
            bg="#28a745",
            fg=Colors.WHITE,
            activebackground="#218838",
            activeforeground=Colors.WHITE,
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_backup_clicked
        )
        self.backup_button.pack(side=tk.LEFT, padx=8)
        
        self.restore_button = tk.Button(
            buttons_frame,
            text="📂 Restore Database",
            font=Fonts.TEXT_BOLD,
            bg="#007bff",
            fg=Colors.WHITE,
            activebackground="#0056b3",
            activeforeground=Colors.WHITE,
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_restore_clicked
        )
        self.restore_button.pack(side=tk.LEFT, padx=8)
        
        self.status_label = tk.Label(
            container_frame,
            text="Ready to backup or restore database",
            font=Fonts.SMALL,
            fg="#AAAAAA",
            bg=Colors.PRIMARY_BG
        )
        self.status_label.pack(pady=(8, 5))
    
    def _on_backup_clicked(self):
        """Handle backup button click."""
        try:
            log_info("backup", "Database backup initiated")
            
            response = messagebox.askyesno(
                "Confirm Database Backup",
                f"This will create a complete backup of the '{AppConfig.DB_DATABASE}' database.\n\n"
                "Do you want to continue?"
            )
            
            if not response:
                log_info("backup", "Database backup cancelled by user")
                return
            
            self.status_label.config(text="Creating database backup...", fg="#FFA500")
            self.backup_button.config(state=tk.DISABLED)
            self.restore_button.config(state=tk.DISABLED)
            self.parent.update_idletasks()
            
            backup_dir = Path(f"C:\\Users\\{os.getlogin()}\\Desktop\\Backup")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            if not StorageChecker.check_storage(str(backup_dir), required_mb=100):
                messagebox.showerror(
                    "Insufficient Storage",
                    "Not enough storage space available for backup.\n\n"
                    "Please free up at least 100 MB and try again."
                )
                self._reset_ui()
                return
            
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            backup_file = backup_dir / f"backup_{timestamp}.sql"
            
            success, message = self.db_ops.backup_database(str(backup_file))
            
            if success:
                file_size_mb = os.path.getsize(backup_file) / (1024 * 1024)
                
                log_info("backup", f"Database backup successful: {backup_file}")
                self.status_label.config(
                    text=f"✅ Backup successful! ({file_size_mb:.2f} MB)",
                    fg="#28a745"
                )
                
                response = messagebox.askyesno(
                    "Backup Successful",
                    f"✅ Database backup created successfully!\n\n"
                    f"File: {backup_file.name}\n"
                    f"Size: {file_size_mb:.2f} MB\n"
                    f"Location: {backup_dir}\n\n"
                    f"Do you want to open the backup folder?",
                    icon='info'
                )
                
                if response:
                    import subprocess
                    subprocess.run(['explorer', str(backup_dir)])
            else:
                log_error("backup", "Database backup failed", Exception(message))
                self.status_label.config(text="❌ Backup failed", fg="#dc3545")
                messagebox.showerror(
                    "Backup Failed",
                    f"Failed to create database backup.\n\n"
                    f"Error: {message}\n\n"
                    "Please check if MySQL is running and credentials are correct."
                )
        
        except Exception as e:
            log_error("backup", "Error during database backup", e)
            self.status_label.config(text="❌ Backup error", fg="#dc3545")
            messagebox.showerror(
                "Backup Error",
                f"An error occurred during backup:\n\n{str(e)}"
            )
        
        finally:
            self._reset_ui()
    
    def _on_restore_clicked(self):
        """Handle restore button click."""
        try:
            log_info("backup", "Database restore initiated")
            
            from tkinter import filedialog
            
            backup_dir = Path(f"C:\\Users\\{os.getlogin()}\\Desktop\\Backup")
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = filedialog.askopenfilename(
                title="Select Database Backup File",
                initialdir=str(backup_dir),
                filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
            )
            
            if not backup_file:
                log_info("backup", "Database restore cancelled - no file selected")
                return
            
            response = messagebox.askyesno(
                "Confirm Database Restore",
                f"⚠️ WARNING ⚠️\n\n"
                f"This will REPLACE all current data in '{AppConfig.DB_DATABASE}' database "
                f"with data from the backup file:\n\n"
                f"{Path(backup_file).name}\n\n"
                "All existing data will be LOST!\n\n"
                "Are you absolutely sure you want to continue?",
                icon='warning'
            )
            
            if not response:
                log_info("backup", "Database restore cancelled by user")
                return
            
            response2 = messagebox.askyesno(
                "Final Confirmation",
                "This is your last chance to cancel.\n\n"
                "Restore database from backup?",
                icon='warning'
            )
            
            if not response2:
                log_info("backup", "Database restore cancelled by user (2nd confirmation)")
                return
            
            self.status_label.config(text="Restoring database from backup...", fg="#FFA500")
            self.backup_button.config(state=tk.DISABLED)
            self.restore_button.config(state=tk.DISABLED)
            self.parent.update_idletasks()
            
            success, message = self.db_ops.restore_database(backup_file)
            
            if success:
                log_info("backup", f"Database restore successful from: {backup_file}")
                self.status_label.config(
                    text="✅ Restore successful!",
                    fg="#28a745"
                )
                
                messagebox.showinfo(
                    "Restore Successful",
                    f"Database restored successfully from:\n\n"
                    f"{Path(backup_file).name}\n\n"
                    "Please restart the application for changes to take effect."
                )
            else:
                log_error("backup", "Database restore failed", Exception(message))
                self.status_label.config(text="❌ Restore failed", fg="#dc3545")
                messagebox.showerror(
                    "Restore Failed",
                    f"Failed to restore database.\n\n"
                    f"Error: {message}\n\n"
                    "Please check if MySQL is running and the backup file is valid."
                )
        
        except Exception as e:
            log_error("backup", "Error during database restore", e)
            self.status_label.config(text="❌ Restore error", fg="#dc3545")
            messagebox.showerror(
                "Restore Error",
                f"An error occurred during restore:\n\n{str(e)}"
            )
        
        finally:
            self._reset_ui()
    
    def _reset_ui(self):
        """Reset UI to ready state."""
        self.backup_button.config(state=tk.NORMAL)
        self.restore_button.config(state=tk.NORMAL)
        if "Backup successful" not in self.status_label.cget("text") and \
           "Restore successful" not in self.status_label.cget("text"):
            self.status_label.config(
                text="Ready to backup or restore database",
                fg="#AAAAAA"
            )
