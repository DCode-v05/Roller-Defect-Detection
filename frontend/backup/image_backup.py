"""
Image Backup Component
Handles inference image copying to external devices
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
import os
import subprocess
import shutil
import psutil
from pathlib import Path
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info


class ImageBackupManager:
    """Manages image backup and copying operations."""
    
    def __init__(self, parent):
        """
        Initialize the image backup manager.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        
        self.src_path_var = tk.StringVar()
        self.dest_path_var = tk.StringVar()
        self.selected_files = []
    
    def create_ui(self, container):
        """
        Create the image backup UI section.
        
        Args:
            container: Container frame to pack into
        """
        src_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        src_frame.pack(fill=tk.X, pady=5)
        
        src_label = tk.Label(
            src_frame,
            text="Source Path:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor=tk.W
        )
        src_label.pack(side=tk.LEFT, padx=5)
        
        src_entry = tk.Entry(
            src_frame,
            textvariable=self.src_path_var,
            font=Fonts.SMALL,
            state='readonly'
        )
        src_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        src_folder_btn = tk.Button(
            src_frame,
            text="Select Folder",
            font=("Arial", 9, "bold"),
            bg="#4A90E2",
            fg=Colors.WHITE,
            command=self._select_source_folder,
            cursor="hand2",
            width=11,
            pady=3
        )
        src_folder_btn.pack(side=tk.LEFT, padx=2)
        
        src_files_btn = tk.Button(
            src_frame,
            text="Select Images",
            font=("Arial", 9, "bold"),
            bg="#7B68EE",
            fg=Colors.WHITE,
            command=self._select_source_files,
            cursor="hand2",
            width=11,
            pady=3
        )
        src_files_btn.pack(side=tk.LEFT, padx=2)
        
        dest_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        dest_frame.pack(fill=tk.X, pady=5)
        
        dest_label = tk.Label(
            dest_frame,
            text="Destination Path:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=15,
            anchor=tk.W
        )
        dest_label.pack(side=tk.LEFT, padx=5)
        
        dest_entry = tk.Entry(
            dest_frame,
            textvariable=self.dest_path_var,
            font=Fonts.SMALL,
            state='readonly'
        )
        dest_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        dest_btn = tk.Button(
            dest_frame,
            text="Select Destination",
            font=("Arial", 9, "bold"),
            bg="#FF8C00",
            fg=Colors.WHITE,
            command=self._select_destination,
            cursor="hand2",
            width=17,
            pady=3
        )
        dest_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        copy_btn_frame.pack(pady=10)
        
        copy_btn = tk.Button(
            copy_btn_frame,
            text="📋 Copy to Destination",
            font=Fonts.TEXT_BOLD,
            bg="#00CED1",
            fg=Colors.WHITE,
            command=self.copy_images,
            cursor="hand2",
            width=25,
            pady=8
        )
        copy_btn.pack()
        
        info_label = tk.Label(
            container,
            text="💡 Select source (folder or multiple images) and destination",
            font=("Arial", 9),
            fg="#AAAAAA",
            bg=Colors.PRIMARY_BG,
            justify=tk.CENTER
        )
        info_label.pack(pady=5)
    
    def _select_source_folder(self):
        """Select source folder containing images."""
        default_path = f"C:\\Users\\{os.getlogin()}\\Desktop\\Inference"
        
        folder_path = filedialog.askdirectory(
            title="Select Source Folder",
            initialdir=default_path if os.path.exists(default_path) else os.path.expanduser("~")
        )
        
        if folder_path:
            self.src_path_var.set(folder_path)
            self.selected_files = []
    
    def _select_source_files(self):
        """Select multiple source image files."""
        default_path = f"C:\\Users\\{os.getlogin()}\\Desktop\\Inference"
        
        file_paths = filedialog.askopenfilenames(
            title="Select Image Files",
            initialdir=default_path if os.path.exists(default_path) else os.path.expanduser("~"),
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            self.selected_files = list(file_paths)
            self.src_path_var.set(f"{len(self.selected_files)} files selected")
            print(f"Selected {len(self.selected_files)} files")
    
    def _select_destination(self):
        """Select destination folder (external drive recommended)."""
        dest_path = filedialog.askdirectory(
            title="Select Destination Folder (External Drive)"
        )
        
        if dest_path:
            self.dest_path_var.set(dest_path)
    
    def copy_images(self):
        """Copy images from source to destination with storage check."""
        try:
            log_info("backup", "Attempting to copy images/backup operation")
            
            src_path = self.src_path_var.get()
            if not src_path and not self.selected_files:
                log_warning("backup", "Copy images failed: No source selected")
                messagebox.showwarning(
                    "No Source Selected",
                    "⚠️ Please select a source folder or image files first."
                )
                return
            
            dest_path = self.dest_path_var.get()
            if not dest_path:
                log_warning("backup", "Copy images failed: No destination selected")
                messagebox.showwarning(
                    "No Destination Selected",
                    "⚠️ Please select a destination folder first."
                )
                return
            
            if not os.path.exists(dest_path):
                log_warning("backup", f"Copy images failed: Destination path does not exist - {dest_path}")
                messagebox.showerror(
                    "Invalid Destination",
                    f"❌ Destination path does not exist:\n{dest_path}"
                )
                return
            
            from .file_operations import FileOperations
            
            files_to_copy = FileOperations.get_files_to_copy(
                src_path, 
                self.selected_files
            )
            
            if not files_to_copy:
                log_info("backup", f"No image files found in source: {src_path}")
                messagebox.showinfo(
                    "No Files Found",
                    "ℹ️ No image files found in the selected source."
                )
                return
            
            total_size = FileOperations.calculate_total_size(files_to_copy)
            file_count = len(files_to_copy)
            size_mb = total_size / (1024 * 1024)
            
            log_info("backup", f"Preparing to copy {file_count} files ({size_mb:.2f} MB) from '{src_path}' to '{dest_path}'")
            
            from .storage_checker import StorageChecker
            
            if not StorageChecker.check_storage_space(dest_path, total_size):
                log_warning("backup", f"Copy cancelled: Insufficient storage space at {dest_path}")
                return
            
            if not self.selected_files:
                folder_name = os.path.basename(src_path)
                final_dest_path = os.path.join(dest_path, folder_name)
                
                if os.path.exists(final_dest_path):
                    overwrite = messagebox.askyesno(
                        "Folder Already Exists",
                        f"⚠️ The folder '{folder_name}' already exists at the destination:\n\n"
                        f"{final_dest_path}\n\n"
                        f"Do you want to overwrite the existing files?\n\n"
                        f"Note: Existing files with the same name will be replaced.",
                        icon='warning'
                    )
                    
                    if not overwrite:
                        log_info("backup", f"Copy cancelled by user - destination folder exists: {final_dest_path}")
                        return
            
            confirm = messagebox.askyesno(
                "Confirm Copy",
                f"📋 Copy Operation Details:\n\n"
                f"Files to copy: {file_count}\n"
                f"Total size: {size_mb:.2f} MB\n"
                f"Destination: {dest_path}\n\n"
                f"Do you want to proceed?"
            )
            
            if not confirm:
                log_info("backup", f"Copy operation cancelled by user - {file_count} files")
                return
            
            from .copy_progress import CopyProgressWindow
            
            log_info("backup", f"Starting copy operation - {file_count} files")
            success_count, actual_dest_path = CopyProgressWindow.copy_files_with_progress(
                self.parent,
                files_to_copy,
                dest_path,
                src_path,
                self.selected_files
            )
            
            if success_count == file_count:
                log_info("backup", f"Copy completed successfully - {success_count}/{file_count} files copied to {actual_dest_path}")
                response = messagebox.askquestion(
                    "Copy Completed",
                    f"✅ Successfully copied {success_count} file(s)!\n\n"
                    f"Total size: {size_mb:.2f} MB\n"
                    f"Destination: {actual_dest_path}\n\n"
                    f"Do you want to open the destination folder?",
                    icon='info'
                )
                
                if response == 'yes':
                    normalized_path = os.path.normpath(actual_dest_path)
                    subprocess.run(['explorer', normalized_path])
            else:
                log_warning("backup", f"Copy completed with errors - {success_count}/{file_count} files copied successfully")
                messagebox.showwarning(
                    "Copy Completed with Errors",
                    f"⚠️ Copied {success_count} out of {file_count} file(s).\n\n"
                    f"Some files may have failed to copy.\n"
                    f"Please check the destination folder."
                )
        
        except Exception as e:
            log_error("backup", f"Error during image copy/backup operation", e)
            messagebox.showerror(
                "Copy Error",
                f"❌ An error occurred during copy:\n\n{str(e)}"
            )
            print(f"Copy error: {e}")
            import traceback
            traceback.print_exc()
