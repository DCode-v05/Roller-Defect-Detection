"""
Action Panel Component
Buttons for generating reports, saving charts, and exporting data
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts


class ActionPanel:
    """Action panel with report generation and export buttons."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize the action panel.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to DiagnosisTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        
    def create(self):
        """Create the action panel UI."""
        container = tk.LabelFrame(
            self.parent,
            text="Actions",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        container.pack(fill=tk.BOTH, expand=True)
        
        inner_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, padx=6, pady=2)
        
        generate_btn = tk.Button(
            inner_frame,
            text="Generate Report",
            font=Fonts.SMALL_BOLD,
            bg="#00FF00",
            fg="#000000",
            command=self.tab.generate_report,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1,
            pady=0
        )
        generate_btn.pack(fill=tk.X, pady=(0, 2))
        
        save_chart_btn = tk.Button(
            inner_frame,
            text="Save Chart",
            font=Fonts.SMALL_BOLD,
            bg="#FFFF00",
            fg="#000000",
            command=self.tab.save_chart,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1,
            pady=0
        )
        save_chart_btn.pack(fill=tk.X, pady=(0, 2))
        
        export_btn = tk.Button(
            inner_frame,
            text="Export to Excel",
            font=Fonts.SMALL_BOLD,
            bg="#FF0000",
            fg="#FFFFFF",
            command=self.tab.export_to_excel,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1,
            pady=0
        )
        export_btn.pack(fill=tk.X, pady=(0, 2))

        self.clear_db_btn = tk.Button(
            inner_frame,
            text="Clear DB",
            font=Fonts.SMALL_BOLD,
            bg="#FF6B6B",
            fg="#FFFFFF",
            command=self.tab.clear_database,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1,
            pady=0
        )
        
        if hasattr(self.tab.app, 'current_role'):
            user_role = self.tab.app.current_role
            if user_role in ['Admin', 'Super Admin']:
                self.clear_db_btn.pack(fill=tk.X, pady=(0, 0))
