"""
Control Panel Component
Report filters and date range selection
"""

import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime, date
from tkcalendar import DateEntry

from frontend.utils.config import AppConfig
from ..utils.styles import Colors, Fonts
from ..utils.db_error_handler import DatabaseErrorHandler


class ControlPanel:
    """Control panel for report filtering."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize the control panel.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to DiagnosisTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        
        self.report_type_var = tk.StringVar(value="Overall")
        self.component_type_var = tk.StringVar(value="Small")
        self.from_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        self.to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        
        self.from_date_entry = None
        self.to_date_entry = None
        
    def create(self):
        """Create the control panel UI with two-column layout."""
        container = tk.LabelFrame(
            self.parent,
            text="Controls",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        container.pack(fill=tk.BOTH, pady=(0, 10))
        
        inner_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.BOTH, padx=8, pady=5)
        
        left_column = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        report_type_label = tk.Label(
            left_column,
            text="Report Type",
            font=Fonts.SMALL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        report_type_label.pack(anchor=tk.W, pady=(0, 2))
        
        report_type_combo = ttk.Combobox(
            left_column,
            textvariable=self.report_type_var,
            values=["Overall", "BF", "OD"],
            state="readonly",
            font=Fonts.SMALL,
            width=12
        )
        report_type_combo.pack(fill=tk.X, pady=(0, 8))
        
        from_date_label = tk.Label(
            left_column,
            text="From Date",
            font=Fonts.SMALL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        from_date_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.from_date_entry = DateEntry(
            left_column,
            textvariable=self.from_date_var,
            font=Fonts.SMALL,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            width=12,
            maxdate=date.today()
        )
        self.from_date_entry.pack(fill=tk.X, pady=(0, 5))
        self.from_date_entry.bind("<<DateEntrySelected>>", self._on_from_date_change)
        
        right_column = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        component_type_label = tk.Label(
            right_column,
            text="Component Type",
            font=Fonts.SMALL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        component_type_label.pack(anchor=tk.W, pady=(0, 2))
        
        roller_types = self._get_roller_types()
        
        roller_types_with_all = ["All"] + roller_types
        
        component_type_combo = ttk.Combobox(
            right_column,
            textvariable=self.component_type_var,
            values=roller_types_with_all,
            state="readonly",
            font=Fonts.SMALL,
            width=12
        )
        component_type_combo.pack(fill=tk.X, pady=(0, 8))
        
        self.component_type_var.set("All")
        
        to_date_label = tk.Label(
            right_column,
            text="To Date",
            font=Fonts.SMALL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        to_date_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.to_date_entry = DateEntry(
            right_column,
            textvariable=self.to_date_var,
            font=Fonts.SMALL,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            width=12,
            maxdate=date.today()
        )
        self.to_date_entry.pack(fill=tk.X, pady=(0, 5))
        self.to_date_entry.bind("<<DateEntrySelected>>", self._on_to_date_change)
    
    def _on_from_date_change(self, event=None):
        """Validate From Date when it changes."""
        try:
            from_date = datetime.strptime(self.from_date_var.get(), '%Y-%m-%d').date()
            to_date = datetime.strptime(self.to_date_var.get(), '%Y-%m-%d').date()
            today = date.today()
            
            if from_date > today:
                self.from_date_var.set(today.strftime('%Y-%m-%d'))
                from_date = today
            
            if from_date > to_date:
                self.to_date_var.set(from_date.strftime('%Y-%m-%d'))
                
        except Exception as e:
            print(f"Error validating from date: {e}")
    
    def _on_to_date_change(self, event=None):
        """Validate To Date when it changes."""
        try:
            from_date = datetime.strptime(self.from_date_var.get(), '%Y-%m-%d').date()
            to_date = datetime.strptime(self.to_date_var.get(), '%Y-%m-%d').date()
            today = date.today()
            
            if to_date > today:
                self.to_date_var.set(today.strftime('%Y-%m-%d'))
                to_date = today
            
            if to_date < from_date:
                self.from_date_var.set(to_date.strftime('%Y-%m-%d'))
                
        except Exception as e:
            print(f"Error validating to date: {e}")
    
    def _get_roller_types(self):
        """Get list of roller types from database."""
        def _fetch_rollers():
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT roller_type FROM roller_data ORDER BY roller_type")
            
            roller_types = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            connection.close()
            
            return roller_types if roller_types else ["Small"]
        
        return DatabaseErrorHandler.safe_db_operation(
            _fetch_rollers,
            parent_widget=self.parent,
            context="fetching roller types",
            default_return=["Small"],
            show_error=True
        )
    
    def get_filters(self):
        """
        Get current filter values with validation.
        
        Returns:
            dict: Dictionary with filter values, or None if validation fails
        """
        try:
            from_date = datetime.strptime(self.from_date_var.get(), '%Y-%m-%d').date()
            to_date = datetime.strptime(self.to_date_var.get(), '%Y-%m-%d').date()
            today = date.today()
            
            if from_date > to_date:
                from tkinter import messagebox
                messagebox.showerror("Invalid Date Range", "From Date must be less than or equal to To Date!")
                return None
            
            if to_date > today:
                from tkinter import messagebox
                messagebox.showerror("Invalid Date", "To Date cannot be in the future!")
                return None
            
            if from_date > today:
                from tkinter import messagebox
                messagebox.showerror("Invalid Date", "From Date cannot be in the future!")
                return None
            
            return {
                'report_type': self.report_type_var.get(),
                'component_type': self.component_type_var.get(),
                'from_date': self.from_date_var.get(),
                'to_date': self.to_date_var.get()
            }
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Invalid Date Format", f"Please enter valid dates in YYYY-MM-DD format.\n{str(e)}")
            return None
