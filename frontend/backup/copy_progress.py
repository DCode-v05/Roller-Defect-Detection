"""
Copy Progress Window
Shows progress during file copy operations
"""

import tkinter as tk
import tkinter.ttk as ttk
import os
import shutil
from ..utils.styles import Fonts


class CopyProgressWindow:
    """Manages copy progress window and file copying."""
    
    @staticmethod
    def copy_files_with_progress(parent, file_list, dest_path, src_path, selected_files):
        """
        Copy files with progress tracking.
        
        Args:
            parent: Parent widget
            file_list: List of source file paths
            dest_path: Destination folder path
            src_path: Source folder path (for structure preservation)
            selected_files: List of selected files (if any)
            
        Returns:
            tuple: (success_count, actual_destination_path)
        """
        success_count = 0
        total_files = len(file_list)
        
        if selected_files:
            actual_dest_path = dest_path
        else:
            folder_name = os.path.basename(src_path)
            actual_dest_path = os.path.join(dest_path, folder_name)
        
        progress_win = tk.Toplevel(parent)
        progress_win.title("Copying Files")
        progress_win.geometry("500x150")
        progress_win.transient(parent)
        progress_win.grab_set()
        
        progress_win.update_idletasks()
        x = (progress_win.winfo_screenwidth() // 2) - (500 // 2)
        y = (progress_win.winfo_screenheight() // 2) - (150 // 2)
        progress_win.geometry(f"500x150+{x}+{y}")
        
        progress_label = tk.Label(
            progress_win,
            text="Preparing to copy...",
            font=Fonts.TEXT,
            pady=10
        )
        progress_label.pack()
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            progress_win,
            variable=progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        progress_bar.pack(pady=10)
        
        status_label = tk.Label(
            progress_win,
            text="0 / 0",
            font=Fonts.SMALL,
            fg="#666666"
        )
        status_label.pack()
        
        for idx, src_file in enumerate(file_list, 1):
            try:
                progress_label.config(text=f"Copying: {os.path.basename(src_file)}")
                status_label.config(text=f"{idx} / {total_files}")
                progress_var.set((idx / total_files) * 100)
                progress_win.update()
                
                if selected_files:
                    dest_file = os.path.join(actual_dest_path, os.path.basename(src_file))
                else:
                    rel_path = os.path.relpath(src_file, src_path)
                    dest_file = os.path.join(actual_dest_path, rel_path)
                
                dest_dir = os.path.dirname(dest_file)
                os.makedirs(dest_dir, exist_ok=True)
                
                shutil.copy2(src_file, dest_file)
                success_count += 1
                
            except Exception as e:
                print(f"Error copying {src_file}: {e}")
                continue
        
        progress_win.destroy()
        
        return success_count, actual_dest_path
