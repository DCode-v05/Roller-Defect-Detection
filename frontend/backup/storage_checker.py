"""
Storage Checker Utility
Checks available storage space before copying
"""

import psutil
from tkinter import messagebox


class StorageChecker:
    """Static methods for storage space checking."""
    
    @staticmethod
    def check_storage(dest_path, required_mb=100):
        """
        Simple storage check for a required amount in MB.
        
        Args:
            dest_path: Destination folder path
            required_mb: Required space in megabytes (default 100 MB)
            
        Returns:
            bool: True if enough space available, False otherwise
        """
        try:
            disk_usage = psutil.disk_usage(dest_path)
            available_mb = disk_usage.free / (1024 * 1024)
            
            return available_mb >= required_mb
        
        except Exception as e:
            print(f"Error checking storage: {e}")
            return True
    
    @staticmethod
    def check_storage_space(dest_path, required_size):
        """
        Check if destination has enough storage space.
        
        Args:
            dest_path: Destination folder path
            required_size: Required size in bytes
            
        Returns:
            bool: True if enough space or user confirms, False otherwise
        """
        try:
            disk_usage = psutil.disk_usage(dest_path)
            
            available_space = disk_usage.free
            required_mb = required_size / (1024 * 1024)
            available_mb = available_space / (1024 * 1024)
            available_gb = available_space / (1024 * 1024 * 1024)
            
            if available_space < (required_size * 1.1):
                messagebox.showerror(
                    "Insufficient Storage",
                    f"❌ Not enough storage space!\n\n"
                    f"Required: {required_mb:.2f} MB\n"
                    f"Available: {available_mb:.2f} MB ({available_gb:.2f} GB)\n\n"
                    f"Please free up space or select a different destination."
                )
                return False
            
            messagebox.showinfo(
                "Storage Check",
                f"✅ Storage Check Passed\n\n"
                f"Required: {required_mb:.2f} MB\n"
                f"Available: {available_mb:.2f} MB ({available_gb:.2f} GB)\n"
                f"After copy: {(available_space - required_size) / (1024**3):.2f} GB remaining"
            )
            
            return True
        
        except Exception as e:
            print(f"Error checking storage: {e}")
            return messagebox.askyesno(
                "Storage Check Failed",
                f"⚠️ Unable to check storage space.\n\n"
                f"Error: {str(e)}\n\n"
                f"Do you want to proceed anyway?"
            )
