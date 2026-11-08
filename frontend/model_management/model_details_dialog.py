"""
Model Details Dialog
Shows detailed information about a selected model including trained classes
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts
from ultralytics import YOLO
import os


class ModelDetailsDialog:
    """Dialog window showing model details."""
    
    def __init__(self, parent, model_data):
        """
        Initialize model details dialog.
        
        Args:
            parent: Parent widget
            model_data: Dictionary containing model information
        """
        self.parent = parent
        self.model_data = model_data
        self.dialog = None
        
    def show(self):
        """Display the details dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Model Details - {self.model_data['model_name']}")
        self.dialog.geometry("900x650")
        self.dialog.configure(bg=Colors.PRIMARY_BG)
        self.dialog.resizable(False, False)
        
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"900x650+{x}+{y}")
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self._create_content()
        
    def _create_content(self):
        """Create dialog content."""
        main_frame = tk.Frame(self.dialog, bg=Colors.PRIMARY_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            main_frame,
            text=f"📋 {self.model_data['model_name']}",
            font=Fonts.TITLE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(0, 15))
        
        content_container = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        left_column = tk.Frame(content_container, bg=Colors.PRIMARY_BG)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        info_frame = tk.LabelFrame(
            left_column,
            text="Model Information",
            font=Fonts.HEADER,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_container = tk.Frame(info_frame, bg=Colors.PRIMARY_BG)
        info_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self._create_info_row(info_container, "Model ID:", str(self.model_data['id']))
        self._create_info_row(info_container, "Model Type:", self.model_data['model_type'])
        self._create_info_row(info_container, "Upload Date:", str(self.model_data['upload_date']))
        self._create_info_row(info_container, "Uploaded By:", self.model_data['uploaded_by'])
        
        file_size = self._get_file_size(self.model_data['model_path'])
        self._create_info_row(info_container, "File Size:", file_size)
        
        path_frame = tk.Frame(info_container, bg=Colors.PRIMARY_BG)
        path_frame.pack(fill=tk.X, pady=8)
        
        path_label = tk.Label(
            path_frame,
            text="File Path:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        path_label.pack(anchor=tk.W)
        
        path_value = tk.Label(
            path_frame,
            text=self.model_data['model_path'],
            font=Fonts.SMALL_BOLD,
            fg="#00bfff",
            bg=Colors.PRIMARY_BG,
            anchor=tk.W,
            wraplength=380,
            justify=tk.LEFT
        )
        path_value.pack(anchor=tk.W, padx=(10, 0))
        
        right_column = tk.Frame(content_container, bg=Colors.PRIMARY_BG)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        classes_frame = tk.LabelFrame(
            right_column,
            text="Trained Classes",
            font=Fonts.HEADER,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        classes_frame.pack(fill=tk.BOTH, expand=True)
        
        self._display_classes(classes_frame)
        
        close_button = tk.Button(
            main_frame,
            text="Close",
            font=Fonts.TEXT_BOLD,
            bg=Colors.INFO,
            fg=Colors.WHITE,
            command=self.dialog.destroy,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            padx=40,
            pady=8
        )
        close_button.pack(pady=(15, 0))
    
    def _create_info_row(self, parent, label_text, value_text):
        """Create an information row."""
        row_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        row_frame.pack(fill=tk.X, pady=8)
        
        label = tk.Label(
            row_frame,
            text=label_text,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        label.pack(anchor=tk.W)
        
        value_label = tk.Label(
            row_frame,
            text=value_text,
            font=Fonts.TEXT_BOLD,
            fg="#00bfff",
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        value_label.pack(anchor=tk.W, padx=(10, 0))
    
    def _get_file_size(self, file_path):
        """Get formatted file size."""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                
                if size_bytes < 1024:
                    return f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.2f} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    return f"{size_bytes / (1024 * 1024):.2f} MB"
                else:
                    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            else:
                return "File not found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _display_classes(self, parent):
        """Load and display model classes."""
        classes_container = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        classes_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        loading_label = tk.Label(
            classes_container,
            text="Loading model classes...",
            font=Fonts.TEXT_BOLD,
            fg="#ffff00",
            bg=Colors.PRIMARY_BG
        )
        loading_label.pack(pady=20)
        
        self.dialog.update()
        
        try:
            model_path = self.model_data['model_path']
            
            if not os.path.exists(model_path):
                loading_label.config(
                    text="❌ Model file not found!",
                    fg="#ff0000"
                )
                return
            
            model = YOLO(model_path)
            
            class_names = model.names
            
            loading_label.destroy()
            
            header_frame = tk.Frame(classes_container, bg=Colors.SECONDARY_BG)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            count_label = tk.Label(
                header_frame,
                text=f"Total Classes: {len(class_names)}",
                font=Fonts.TEXT_BOLD,
                fg="#00ff00",
                bg=Colors.SECONDARY_BG,
                padx=10,
                pady=5
            )
            count_label.pack()
            
            classes_grid_frame = tk.Frame(classes_container, bg=Colors.PRIMARY_BG)
            classes_grid_frame.pack(fill=tk.BOTH, expand=True)
            
            col_count = 2
            row = 0
            col = 0
            
            for class_id, class_name in class_names.items():
                class_frame = tk.Frame(
                    classes_grid_frame,
                    bg=Colors.SECONDARY_BG,
                    bd=1,
                    relief=tk.RAISED
                )
                class_frame.grid(row=row, column=col, padx=5, pady=4, sticky="ew")
                
                inner = tk.Frame(class_frame, bg=Colors.SECONDARY_BG)
                inner.pack(fill=tk.X, padx=8, pady=4)
                
                class_text = tk.Label(
                    inner,
                    text=f"[{class_id}]  {class_name}",
                    font=Fonts.TEXT_BOLD,
                    fg=Colors.WHITE,
                    bg=Colors.SECONDARY_BG,
                    anchor=tk.W
                )
                class_text.pack(anchor=tk.W)
                
                col += 1
                if col >= col_count:
                    col = 0
                    row += 1
            
            for i in range(col_count):
                classes_grid_frame.grid_columnconfigure(i, weight=1, uniform="classes")
            
        except Exception as e:
            loading_label.config(
                text=f"❌ Error loading model:\n{str(e)}",
                fg="#ff0000",
                font=Fonts.SMALL_BOLD
            )
            print(f"❌ Error loading model classes: {e}")
            import traceback
            traceback.print_exc()
