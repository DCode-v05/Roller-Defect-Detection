"""
Upload Section Component
Handles model upload form with name, type, and file selection
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info
from .model_database import ModelDatabase


class UploadSection:
    """Upload section for new models."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize upload section.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to ModelManagementTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        self.model_name_var = None
        self.model_type_var = None
        self.selected_file_path = None
        self.file_label = None
        
    def create(self):
        """Create the upload section UI."""
        upload_frame = tk.LabelFrame(
            self.parent,
            text="Upload New Model",
            font=Fonts.HEADER,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        upload_frame.pack(fill=tk.X, pady=(0, 10))
        
        inner_frame = tk.Frame(upload_frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.X, padx=20, pady=15)
        
        left_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        left_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        name_label = tk.Label(
            left_frame,
            text="Model Name:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.model_name_var = tk.StringVar()
        name_entry = tk.Entry(
            left_frame,
            textvariable=self.model_name_var,
            font=Fonts.TEXT_BOLD,
            width=25,
            bg="#FFFFFF",
            fg="#000000"
        )
        name_entry.pack()
        
        middle_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        middle_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        type_label = tk.Label(
            middle_frame,
            text="Model Type:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        type_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.model_type_var = tk.StringVar(value="BIGFACE")
        
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.configure(
            "Custom.TCombobox",
            fieldbackground="#FFFFFF",
            background=Colors.INFO,
            foreground="#000000",
            selectbackground=Colors.INFO,
            selectforeground="#FFFFFF"
        )
        
        type_dropdown = ttk.Combobox(
            middle_frame,
            textvariable=self.model_type_var,
            values=["BIGFACE", "OD"],
            state="readonly",
            font=Fonts.TEXT_BOLD,
            width=22,
            style="Custom.TCombobox"
        )
        type_dropdown.pack()
        
        right_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        right_frame.pack(side=tk.LEFT)
        
        spacer = tk.Label(
            right_frame,
            text="",
            font=Fonts.TEXT,
            bg=Colors.PRIMARY_BG
        )
        spacer.pack(pady=(0, 5))
        
        upload_button = tk.Button(
            right_frame,
            text="Browse & Upload Model",
            font=Fonts.TEXT_BOLD,
            bg=Colors.INFO,
            fg=Colors.WHITE,
            command=self._browse_and_upload,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=5
        )
        upload_button.pack()
        
        self.file_label = tk.Label(
            upload_frame,
            text="No file selected",
            font=Fonts.SMALL_BOLD,
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        self.file_label.pack(pady=(0, 10))
    
    def _browse_and_upload(self):
        """Browse for model file and upload."""
        model_name = self.model_name_var.get().strip()
        model_type = self.model_type_var.get()
        
        if not model_name:
            messagebox.showerror("Error", "Please enter a model name!")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[
                ("PyTorch Model", "*.pt"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        file_name = os.path.basename(file_path)
        self.file_label.config(text=f"Selected: {file_name}", fg="#00ff00")
        
        self._upload_model(model_name, model_type, file_path)
    
    def _upload_model(self, model_name, model_type, source_file):
        """
        Upload model to storage and database.
        
        Args:
            model_name: Name of the model
            model_type: Type (BIGFACE or OD)
            source_file: Source file path
        """
        try:
            log_info("model_management", f"Attempting to upload model - Name: {model_name}, Type: {model_type}")
            
            username = os.getlogin()
            dest_dir = f"C:\\Users\\{username}\\Desktop\\Models\\{model_type}"
            os.makedirs(dest_dir, exist_ok=True)
            
            base_name = os.path.basename(source_file)
            dest_path = os.path.join(dest_dir, base_name)
            
            log_info("model_management", f"Copying model file to: {dest_path}")
            shutil.copy2(source_file, dest_path)
            
            db = ModelDatabase()
            if db.connect():
                uploaded_by = self.tab.app.current_user if hasattr(self.tab.app, 'current_user') else "Unknown"
                
                success = db.insert_model(
                    model_name=model_name,
                    model_type=model_type,
                    model_path=dest_path,
                    uploaded_by=uploaded_by
                )
                
                db.disconnect()
                
                if success:
                    log_info("model_management", f"Model '{model_name}' uploaded successfully by user '{uploaded_by}' - Path: {dest_path}")
                    messagebox.showinfo(
                        "Success",
                        f"Model '{model_name}' uploaded successfully!\n\nSaved to: {dest_path}"
                    )
                    
                    self.model_name_var.set("")
                    self.file_label.config(text="No file selected", fg="#888888")
                    
                    self.tab.refresh_models()
                    
                    if hasattr(self.tab, 'app'):
                        self.tab.app.reload_models_and_notify_tabs()
                else:
                    log_error("model_management", f"Failed to save model '{model_name}' to database")
                    messagebox.showerror("Error", "Failed to save model to database!")
            else:
                log_error("model_management", f"Failed to connect to database for model upload - {model_name}")
                messagebox.showerror("Error", "Failed to connect to database!")
                
        except Exception as e:
            log_error("model_management", f"Error uploading model '{model_name}' (Type: {model_type})", e)
            messagebox.showerror("Error", f"Failed to upload model:\n{str(e)}")
            print(f"❌ Upload error: {e}")
            import traceback
            traceback.print_exc()
