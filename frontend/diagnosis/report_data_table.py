"""
Report Data Table Component
Displays inspection data in a scrollable table
"""

import tkinter as tk
import tkinter.ttk as ttk
from ..utils.styles import Colors, Fonts


class ReportDataTable:
    """Table displaying report data."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize the report data table.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to DiagnosisTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        self.tree = None
        self.container = None
        self.current_columns = []
        
    def create(self):
        """Create the report data table UI."""
        self.container = tk.LabelFrame(
            self.parent,
            text="Report Data",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE,
            width=700
        )
        self.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.container.pack_propagate(False)
        
        self.tree_frame = tk.Frame(self.container, bg=Colors.PRIMARY_BG)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.v_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.h_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        
        self._create_tree_for_report_type("Overall")
    
    def _create_tree_for_report_type(self, report_type):
        """Create treeview with columns based on report type."""
        if report_type == "BF":
            columns = (
                "S.No", "Component Type", "Employee ID", "Report Date", "Start Time", "End Time",
                "BF Inspected", "BF Accepted", "BF Rejected", "Acceptance Rate",
                "Rust", "Damage", "Dent", "High Head", "Down Head", "Others"
            )
            column_widths = {
                "S.No": 50, "Component Type": 120, "Employee ID": 100, "Report Date": 100,
                "Start Time": 90, "End Time": 90, "BF Inspected": 100,
                "BF Accepted": 100, "BF Rejected": 100, "Acceptance Rate": 110,
                "Rust": 80, "Damage": 80, "Dent": 80, "High Head": 90,
                "Down Head": 90, "Others": 80
            }
        elif report_type == "OD":
            columns = (
                "S.No", "Component Type", "Employee ID", "Report Date", "Start Time", "End Time",
                "OD Inspected", "OD Accepted", "OD Rejected", "Acceptance Rate",
                "Rust", "Damage", "Dent", "Damage on End", "Spherical Mark", "Others"
            )
            column_widths = {
                "S.No": 50, "Component Type": 120, "Employee ID": 100, "Report Date": 100,
                "Start Time": 90, "End Time": 90, "OD Inspected": 100,
                "OD Accepted": 100, "OD Rejected": 100, "Acceptance Rate": 110,
                "Rust": 80, "Damage": 80, "Dent": 80, "Damage on End": 110,
                "Spherical Mark": 110, "Others": 80
            }
        else:
            columns = (
                "S.No", "Component Type", "Employee ID", "Report Date", "Start Time", "End Time",
                "Overall Inspected", "Overall Accepted", "Overall Rejected", "Acceptance Rate",
                "BF Inspected", "BF Accepted", "BF Rejected",
                "OD Inspected", "OD Accepted", "OD Rejected"
            )
            column_widths = {
                "S.No": 50, "Component Type": 120, "Employee ID": 100, "Report Date": 100,
                "Start Time": 90, "End Time": 90, "Overall Inspected": 120,
                "Overall Accepted": 120, "Overall Rejected": 120, "Acceptance Rate": 110,
                "BF Inspected": 100, "BF Accepted": 100, "BF Rejected": 100,
                "OD Inspected": 100, "OD Accepted": 100, "OD Rejected": 100
            }
        
        self.current_columns = columns
        
        if self.tree:
            self.tree.destroy()
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set,
            selectmode="browse"
        )
        
        self.v_scrollbar.config(command=self.tree.yview)
        self.h_scrollbar.config(command=self.tree.xview)
        
        for col in columns:
            self.tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER)
            self.tree.heading(col, text=col, anchor=tk.CENTER)
        
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#000000",
            rowheight=25,
            fieldbackground="#FFFFFF",
            font=Fonts.SMALL
        )
        
        style.configure(
            "Treeview.Heading",
            background=Colors.SECONDARY_BG,
            foreground=Colors.WHITE,
            font=Fonts.SMALL_BOLD,
            borderwidth=1
        )
        
        style.map("Treeview", background=[("selected", Colors.PRIMARY_BLUE)])
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
    
    def update_data(self, data, report_type):
        """
        Update table with new data.
        
        Args:
            data: List of dictionaries with report data
            report_type: Type of report (BF, OD, Overall)
        """
        self._create_tree_for_report_type(report_type)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        totals = {}
        for col in self.current_columns:
            totals[col] = 0
        
        for idx, row in enumerate(data, start=1):
            values = []
            for col in self.current_columns:
                if col == "S.No":
                    val = idx
                else:
                    val = row.get(col, 0)
                values.append(val)
                
                if col not in ["S.No", "Component Type", "Employee ID", "Report Date", "Start Time", "End Time", "Acceptance Rate"]:
                    try:
                        if isinstance(val, str) and '%' in val:
                            continue
                        totals[col] += int(val) if val else 0
                    except:
                        pass
            
            self.tree.insert("", tk.END, values=values)
        
        if data:
            total_values = []
            for col in self.current_columns:
                if col == "S.No":
                    total_values.append("")
                elif col == "Component Type":
                    total_values.append("TOTAL")
                elif col in ["Employee ID", "Report Date", "Start Time", "End Time"]:
                    total_values.append("")
                elif col == "Acceptance Rate":
                    if report_type == "BF":
                        inspected = totals.get("BF Inspected", 0)
                        accepted = totals.get("BF Accepted", 0)
                    elif report_type == "OD":
                        inspected = totals.get("OD Inspected", 0)
                        accepted = totals.get("OD Accepted", 0)
                    else:
                        inspected = totals.get("Overall Inspected", 0)
                        accepted = totals.get("Overall Accepted", 0)
                    
                    rate = (accepted / inspected * 100) if inspected > 0 else 0
                    total_values.append(f"{rate:.2f}%")
                else:
                    total_values.append(totals.get(col, 0))
            
            total_item = self.tree.insert("", tk.END, values=total_values, tags=('total',))
            
            self.tree.tag_configure('total', background='#E0E0E0', font=Fonts.SMALL_BOLD)
