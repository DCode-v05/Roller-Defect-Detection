"""
Model Management Tab - Main Controller
Handles AI model upload, viewing, and deletion
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info
from .upload_section import UploadSection
from .models_table import ModelsTable
from .model_actions import ModelActions


class ModelManagementTab:
    """Model Management tab for uploading and managing AI models."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the model management tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.upload_section = None
        self.models_table = None
        self.model_actions = None
        
    def setup(self):
        """Setup the model management tab UI."""
        try:
            log_info("model_management", "Setting up Model Management tab")
            
            main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
            main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            title_label = tk.Label(
                main_container,
                text="AI Model Management",
                font=Fonts.TITLE,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG
            )
            title_label.pack(pady=(0, 10))
            
            self.upload_section = UploadSection(main_container, self)
            self.upload_section.create()
            
            models_frame = tk.LabelFrame(
                main_container,
                text="📦 Loaded Models",
                font=Fonts.HEADER,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG,
                bd=2,
                relief=tk.RIDGE
            )
            models_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
            
            self.models_table = ModelsTable(models_frame, self)
            self.models_table.create()
            
            self.model_actions = ModelActions(main_container, self)
            self.model_actions.create()
            
            self.refresh_models()
            
            log_info("model_management", "Model Management tab setup completed successfully")
        except Exception as e:
            log_error("model_management", "Failed to setup Model Management tab", e)
            raise
    
    def refresh_models(self):
        """Refresh the models table with latest data from database."""
        if self.models_table:
            self.models_table.load_models()
    
    def get_selected_model(self):
        """Get the currently selected model from the table."""
        if self.models_table:
            return self.models_table.get_selected_model()
        return None
