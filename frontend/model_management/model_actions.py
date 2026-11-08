"""
Model Actions Component
Handles view details and delete model operations
"""

import tkinter as tk
from tkinter import messagebox
import os
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info
from .model_database import ModelDatabase
from .model_details_dialog import ModelDetailsDialog


class ModelActions:
    """Action buttons for model operations."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize model actions.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to ModelManagementTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        
    def create(self):
        """Create the action buttons UI."""
        actions_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        actions_frame.pack(fill=tk.X, pady=(5, 5))
        
        info_label = tk.Label(
            actions_frame,
            text="💡 Double-click on any model to view details",
            font=Fonts.TEXT_BOLD,
            fg="#ffff00",
            bg=Colors.PRIMARY_BG
        )
        info_label.pack(side=tk.LEFT, padx=5)
        
        delete_button = tk.Button(
            actions_frame,
            text="Delete Model",
            font=Fonts.TEXT_BOLD,
            bg=Colors.DANGER,
            fg=Colors.WHITE,
            command=self._delete_model,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            padx=25,
            pady=5
        )
        delete_button.pack(side=tk.RIGHT, padx=5)
    
    def _delete_model(self):
        """Delete selected model."""
        try:
            model = self.tab.get_selected_model()
            
            if not model:
                log_warning("model_management", "Delete model failed: No model selected")
                messagebox.showwarning("No Selection", "Please select a model to delete!")
                return
            
            log_info("model_management", f"Attempting to delete model - Name: {model['model_name']}, Type: {model['model_type']}, ID: {model['id']}")
            
            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete the model:\n\n"
                f"Name: {model['model_name']}\n"
                f"Type: {model['model_type']}\n\n"
                f"This will remove the database entry and delete the model file.\n"
                f"This action cannot be undone!"
            )
            
            if not confirm:
                log_info("model_management", f"Model deletion cancelled by user - {model['model_name']}")
                return
            
            db = ModelDatabase()
            if db.connect():
                success = db.delete_model(model['id'], model['model_type'])
                db.disconnect()
                
                if success:
                    try:
                        if os.path.exists(model['model_path']):
                            os.remove(model['model_path'])
                            log_info("model_management", f"Model file deleted from disk: {model['model_path']}")
                    except Exception as e:
                        log_warning("model_management", f"Could not delete model file from disk: {model['model_path']}", e)
                        print(f"⚠ Warning: Could not delete file: {e}")
                    
                    log_info("model_management", f"Model '{model['model_name']}' (ID: {model['id']}) deleted successfully")
                    messagebox.showinfo(
                        "Success",
                        f"Model '{model['model_name']}' deleted successfully!"
                    )
                    
                    self.tab.refresh_models()
                    
                    if hasattr(self.tab, 'app'):
                        self.tab.app.reload_models_and_notify_tabs()
                else:
                    log_error("model_management", f"Failed to delete model '{model['model_name']}' from database")
                    messagebox.showerror("Error", "Failed to delete model from database!")
            else:
                log_error("model_management", f"Failed to connect to database for model deletion - {model['model_name']}")
                messagebox.showerror("Error", "Failed to connect to database!")
                
        except Exception as e:
            log_error("model_management", f"Error deleting model", e)
            messagebox.showerror("Error", f"Failed to delete model:\n{str(e)}")
            print(f"❌ Delete error: {e}")
            import traceback
            traceback.print_exc()
