"""
Models Table Component
Displays loaded models in a scrollable table
"""

import tkinter as tk
from tkinter import ttk
from ..utils.styles import Colors, Fonts
from .model_database import ModelDatabase


class ModelsTable:
    """Table displaying loaded models."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize models table.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to ModelManagementTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        self.tree = None
        self.filter_var = None
        
    def create(self):
        """Create the models table UI."""
        filter_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        filter_label = tk.Label(
            filter_frame,
            text="Filter by Type:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        filter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_var = tk.StringVar(value="ALL")
        
        radio_frame = tk.Frame(filter_frame, bg=Colors.PRIMARY_BG)
        radio_frame.pack(side=tk.LEFT)
        
        for option in [("ALL", "ALL"), ("BIGFACE", "BIGFACE"), ("OD", "OD")]:
            rb = tk.Radiobutton(
                radio_frame,
                text=option[0],
                variable=self.filter_var,
                value=option[1],
                font=Fonts.TEXT_BOLD,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG,
                selectcolor=Colors.PRIMARY_BG,
                activebackground=Colors.PRIMARY_BG,
                activeforeground=Colors.WHITE,
                command=self.load_models
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        refresh_button = tk.Button(
            filter_frame,
            text="Refresh",
            font=Fonts.SMALL_BOLD,
            bg=Colors.INFO,
            fg=Colors.WHITE,
            command=self.load_models,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1,
            padx=15,
            pady=2
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        table_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("ID", "Name", "Type", "Model Path", "Upload Date", "Uploaded By")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=8
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Name", width=200, anchor=tk.W)
        self.tree.column("Type", width=100, anchor=tk.CENTER)
        self.tree.column("Model Path", width=400, anchor=tk.W)
        self.tree.column("Upload Date", width=150, anchor=tk.CENTER)
        self.tree.column("Uploaded By", width=150, anchor=tk.CENTER)
        
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
        
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#000000",
            rowheight=25,
            fieldbackground="#FFFFFF",
            font=Fonts.TEXT_BOLD
        )
        
        style.configure(
            "Treeview.Heading",
            background=Colors.SECONDARY_BG,
            foreground=Colors.WHITE,
            font=Fonts.TEXT_BOLD,
            relief=tk.RAISED
        )
        
        style.map(
            "Treeview",
            background=[("selected", Colors.INFO)],
            foreground=[("selected", Colors.WHITE)]
        )
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind("<Double-1>", self._on_double_click)
        
        self.status_label = tk.Label(
            self.parent,
            text="Ready",
            font=Fonts.TEXT_BOLD,
            fg="#00ff00",
            bg=Colors.PRIMARY_BG
        )
        self.status_label.pack(pady=(5, 0))
    
    def _on_double_click(self, event):
        """Handle double-click on a model to show details."""
        selection = self.tree.selection()
        if not selection:
            return
        
        model = self.get_selected_model()
        if not model:
            return
        
        from .model_details_dialog import ModelDetailsDialog
        import os
        
        if not os.path.exists(model['model_path']):
            from tkinter import messagebox
            messagebox.showerror(
                "File Not Found",
                f"Model file not found at:\n{model['model_path']}\n\nThe file may have been moved or deleted."
            )
            return
        
        dialog = ModelDetailsDialog(self.parent, model)
        dialog.show()
    
    def load_models(self):
        """Load models from database and populate table."""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            filter_type = self.filter_var.get()
            
            db = ModelDatabase()
            if db.connect():
                models = db.get_all_models(filter_type if filter_type != "ALL" else None)
                db.disconnect()
                
                for model in models:
                    self.tree.insert(
                        "",
                        tk.END,
                        values=(
                            model['id'],
                            model['model_name'],
                            model['model_type'],
                            model['model_path'],
                            model['upload_date'],
                            model['uploaded_by']
                        )
                    )
                
                count = len(models)
                self.status_label.config(
                    text=f"Loaded {count} model(s)",
                    fg="#00ff00"
                )
            else:
                self.status_label.config(
                    text="Failed to connect to database",
                    fg="#ff0000"
                )
                
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.status_label.config(
                text=f"Error: {str(e)}",
                fg="#ff0000"
            )
            import traceback
            traceback.print_exc()
    
    def get_selected_model(self):
        """
        Get currently selected model.
        
        Returns:
            dict: Model data or None if no selection
        """
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if not values:
            return None
        
        return {
            'id': values[0],
            'model_name': values[1],
            'model_type': values[2],
            'model_path': values[3],
            'upload_date': values[4],
            'uploaded_by': values[5]
        }
