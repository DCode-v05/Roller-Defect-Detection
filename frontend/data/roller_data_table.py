"""
Roller Data Table
Displays all roller configurations in a scrollable table
"""

import tkinter as tk
from tkinter import ttk
from ..utils.styles import Colors, Fonts
from .data_database import DataDatabase


class RollerDataTable:
    """Table widget for displaying roller data."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the roller data table.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        self.db = DataDatabase()
        
        self.tree = None
        
    def create(self):
        """Create the roller data table UI."""
        main_frame = tk.LabelFrame(
            self.parent,
            text="Roller Data",
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        tree_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        columns = (
            "ID", "Roller Type", "Outer Diameter (mm)", "Dimple Diameter (mm)",
            "Small Diameter (mm)", "Length (mm)", "High Head (pixels)", "Down Head (pixels)"
        )
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=8
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        column_widths = {
            "ID": 50,
            "Roller Type": 150,
            "Outer Diameter (mm)": 150,
            "Dimple Diameter (mm)": 150,
            "Small Diameter (mm)": 150,
            "Length (mm)": 120,
            "High Head (pixels)": 130,
            "Down Head (pixels)": 130
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#FFFFFF",
                       foreground="#000000",
                       fieldbackground="#FFFFFF",
                       rowheight=25)
        style.configure("Treeview.Heading",
                       background=Colors.PRIMARY_BG,
                       foreground=Colors.WHITE,
                       font=Fonts.SMALL_BOLD)
        style.map("Treeview",
                 background=[("selected", "#007BFF")])
        
        self.tree.bind("<Double-1>", self._on_double_click)
    
    def load_roller_data(self):
        """Load roller data from database into table."""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            rollers = self.db.get_all_rollers()
            
            for roller in rollers:
                self.tree.insert("", tk.END, values=(
                    roller['id'],
                    roller['roller_type'],
                    roller['outer_diameter'],
                    roller['dimple_diameter'],
                    roller['small_diameter'],
                    roller['length_mm'],
                    roller['high_head_pixels'],
                    roller['down_head_pixels']
                ))
        
        except Exception as e:
            print(f"❌ Error loading roller data: {e}")
    
    def get_selected_roller(self):
        """Get the currently selected roller from table."""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        return {
            'id': values[0],
            'roller_type': values[1],
            'outer_diameter': values[2],
            'dimple_diameter': values[3],
            'small_diameter': values[4],
            'length_mm': values[5],
            'high_head_pixels': values[6],
            'down_head_pixels': values[7]
        }
    
    def _on_double_click(self, event):
        """Handle double-click on table row."""
        selected = self.get_selected_roller()
        if selected and hasattr(self.app, 'data_tab') and self.app.data_tab:
            if self.app.data_tab.roller_info_panel:
                self.app.data_tab.roller_info_panel.load_roller_data(selected)
