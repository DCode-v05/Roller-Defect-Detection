"""
Settings History Component
Displays history of threshold configuration changes from BF/OD threshold tables
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date
import pandas as pd
import os
from ..utils.styles import Colors, Fonts
from ..utils.permissions import Permissions
from .info_database import InfoDatabase


class SettingsHistory:
    """Component for displaying threshold settings change history."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the settings history component.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        self.db = InfoDatabase()
        
        self.tree = None
        self.from_date_entry = None
        self.to_date_entry = None
        self.filter_var = None
        self.current_data = []
    
    def create(self):
        """Create the settings history UI."""
        main_frame = tk.LabelFrame(
            self.parent,
            text="Settings History",
            font=Fonts.HEADER,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        filter_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            filter_frame,
            text="Filter:",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="Overall")
        filter_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["BF", "OD", "Overall"],
            state="readonly",
            width=10,
            font=Fonts.TEXT
        )
        filter_dropdown.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            filter_frame,
            text="From:",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(15, 5))
        
        self.from_date_entry = DateEntry(
            filter_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            maxdate=date.today()
        )
        self.from_date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            filter_frame,
            text="To:",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(15, 5))
        
        self.to_date_entry = DateEntry(
            filter_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            maxdate=date.today()
        )
        self.to_date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="🔍 Load History",
            font=Fonts.TEXT_BOLD,
            bg="#17A2B8",
            fg=Colors.WHITE,
            activebackground="#117a8b",
            activeforeground=Colors.WHITE,
            command=self.load_history,
            width=12,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        buttons_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="�️ View Details",
            font=Fonts.TEXT_BOLD,
            bg="#6F42C1",
            fg=Colors.WHITE,
            activebackground="#59359a",
            activeforeground=Colors.WHITE,
            command=self.view_details,
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="📊 Export to Excel",
            font=Fonts.TEXT_BOLD,
            bg="#28A745",
            fg=Colors.WHITE,
            activebackground="#218838",
            activeforeground=Colors.WHITE,
            command=self.export_to_excel,
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        user_role = getattr(self.app, 'current_role', 'Operator')
        if Permissions.can_manage_users(user_role):
            tk.Button(
                buttons_frame,
                text="🗑️ Clear History",
                font=Fonts.TEXT_BOLD,
                bg="#DC3545",
                fg=Colors.WHITE,
                activebackground="#c82333",
                activeforeground=Colors.WHITE,
                command=self.clear_history,
                width=15,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
        
        tree_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "type", "model_name", "employee_id", "timestamp", "model_threshold"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=10
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("model_name", text="Model Name")
        self.tree.heading("employee_id", text="Changed By")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("model_threshold", text="Model Threshold")
        
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("type", width=80, anchor=tk.CENTER)
        self.tree.column("model_name", width=200, anchor=tk.W)
        self.tree.column("employee_id", width=150, anchor=tk.CENTER)
        self.tree.column("timestamp", width=180, anchor=tk.CENTER)
        self.tree.column("model_threshold", width=120, anchor=tk.CENTER)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=Colors.WHITE,
            foreground=Colors.PRIMARY_BG,
            fieldbackground=Colors.WHITE,
            rowheight=25
        )
        style.configure("Treeview.Heading", font=Fonts.TEXT_BOLD)
        style.map("Treeview", background=[("selected", "#007BFF")])
        
        self.load_history()
    
    def load_history(self):
        """Load threshold settings history from database based on filters."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_data = []
        
        try:
            filter_type = self.filter_var.get()
            from_date = self.from_date_entry.get_date()
            to_date = self.to_date_entry.get_date()
            
            today = date.today()
            
            if from_date > to_date:
                messagebox.showerror(
                    "Invalid Date Range",
                    "From date cannot be greater than To date.\n\n"
                    "Please select a valid date range."
                )
                return
            
            if to_date > today:
                messagebox.showerror(
                    "Invalid Date",
                    "To date cannot be in the future.\n\n"
                    f"Today's date is: {today.strftime('%Y-%m-%d')}"
                )
                return
            
            if from_date > today:
                messagebox.showerror(
                    "Invalid Date",
                    "From date cannot be in the future.\n\n"
                    f"Today's date is: {today.strftime('%Y-%m-%d')}"
                )
                return
            
            history = self.db.get_threshold_history(filter_type, from_date, to_date)
            
            if not history:
                self.tree.insert(
                    "",
                    tk.END,
                    values=("", "No History", "No threshold changes recorded", "", "", "")
                )
            else:
                for record in history:
                    record_id, record_type, model_name, employee_id, timestamp, defect_threshold, size_threshold, model_threshold = record
                    
                    self.tree.insert(
                        "",
                        tk.END,
                        values=(
                            record_id,
                            record_type,
                            model_name,
                            employee_id,
                            timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "-",
                            f"{float(model_threshold)*100:.0f}%"
                        )
                    )
                    
                    self.current_data.append({
                        'id': record_id,
                        'type': record_type,
                        'model_name': model_name,
                        'employee_id': employee_id,
                        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "-",
                        'model_threshold': f"{float(model_threshold)*100:.0f}%",
                        'defect_threshold': defect_threshold,
                        'size_threshold': size_threshold
                    })
        
        except Exception as e:
            print(f"❌ Error loading threshold history: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load threshold history:\n{str(e)}")
    
    def view_details(self):
        """View detailed information for selected history record."""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a history record to view details.")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if not values or values[0] == "":
            messagebox.showinfo("No Data", "No details available for this record.")
            return
        
        record_id = values[0]
        
        record = None
        for data in self.current_data:
            if data['id'] == record_id:
                record = data
                break
        
        if not record:
            messagebox.showerror("Error", "Record details not found.")
            return
        
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Threshold History Details - ID: {record_id}")
        details_window.geometry("700x500")
        details_window.configure(bg=Colors.PRIMARY_BG)
        
        details_window.transient(self.parent)
        details_window.grab_set()
        
        tk.Label(
            details_window,
            text=f"Threshold Configuration Details",
            font=Fonts.SUBTITLE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(pady=10)
        
        details_frame = tk.Frame(details_window, bg=Colors.PRIMARY_BG)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_text = f"""ID: {record['id']}
Type: {record['type']}
Model Name: {record['model_name']}
Changed By: {record['employee_id']}
Timestamp: {record['timestamp']}
Model Threshold: {record['model_threshold']}

Defect Confidence Thresholds:
"""
        
        defect_str = record['defect_threshold']
        defect_lines = defect_str.replace(', ', '\n  ')
        info_text += f"  {defect_lines}"
        
        info_text += "\n\nDefect Size Thresholds (Bounding Box Area):\n"
        size_str = record.get('size_threshold', '')
        if size_str:
            size_pairs = size_str.split(', ')
            formatted_sizes = []
            for pair in size_pairs:
                if ':' in pair:
                    name, value = pair.split(':')
                    formatted_sizes.append(f"{name}:{value} px²")
            size_lines = '\n  '.join(formatted_sizes)
            info_text += f"  {size_lines}"
        else:
            info_text += "  Not configured"
        
        text_frame = tk.Frame(details_frame, bg=Colors.PRIMARY_BG)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame,
            font=("Consolas", 10),
            bg=Colors.WHITE,
            fg=Colors.PRIMARY_BG,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(
            details_window,
            text="Close",
            font=Fonts.TEXT_BOLD,
            bg="#6C757D",
            fg=Colors.WHITE,
            command=details_window.destroy,
            width=15,
            cursor="hand2"
        ).pack(pady=10)
    
    def export_to_excel(self):
        """Export threshold history to Excel file."""
        import subprocess
        from tkinter import messagebox
        
        if not self.current_data:
            messagebox.showwarning(
                "No Data",
                "No data found for the applied filters.\n\n"
                "Please load threshold history first before exporting."
            )
            return
        
        try:
            filter_type = self.filter_var.get()
            from_date_obj = self.from_date_entry.get_date()
            to_date_obj = self.to_date_entry.get_date()
            
            today = date.today()
            
            if from_date_obj > to_date_obj:
                messagebox.showerror(
                    "Invalid Date Range",
                    "From date cannot be greater than To date."
                )
                return
            
            if to_date_obj > today:
                messagebox.showerror(
                    "Invalid Date",
                    f"To date cannot be in the future.\n\nToday's date is: {today.strftime('%Y-%m-%d')}"
                )
                return
            
            if from_date_obj > today:
                messagebox.showerror(
                    "Invalid Date",
                    f"From date cannot be in the future.\n\nToday's date is: {today.strftime('%Y-%m-%d')}"
                )
                return
            
            from_date = from_date_obj.strftime("%Y-%m-%d")
            to_date = to_date_obj.strftime("%Y-%m-%d")
            
            username = os.getlogin()
            base_path = f"C:\\Users\\{username}\\Desktop\\Threshold Settings\\{filter_type}"
            os.makedirs(base_path, exist_ok=True)
            
            filename = f"{from_date}_{to_date}.xlsx"
            filepath = os.path.join(base_path, filename)
            
            export_data = []
            for record in self.current_data:
                export_data.append({
                    'ID': record['id'],
                    'Type': record['type'],
                    'Model Name': record['model_name'],
                    'Changed By': record['employee_id'],
                    'Timestamp': record['timestamp'],
                    'Model Threshold': record['model_threshold'],
                    'Defect Confidence Thresholds': record['defect_threshold'],
                    'Defect Size Thresholds': record.get('size_threshold', 'Not configured')
                })
            
            df = pd.DataFrame(export_data)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Threshold History')
                
                worksheet = writer.sheets['Threshold History']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            result = messagebox.askquestion(
                "Export Success",
                f"Threshold history exported successfully!\n\n"
                f"File Location:\n{filepath}\n\n"
                f"Do you want to open the folder location?",
                icon='info'
            )
            
            if result == 'yes':
                subprocess.run(['explorer', base_path])
        
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Export Error", f"Failed to export threshold history:\n{str(e)}")
    
    def clear_history(self):
        """Clear threshold history for selected filter type (Admin and Super Admin only)."""
        user_role = getattr(self.app, 'current_role', 'Operator')
        if not Permissions.can_manage_users(user_role):
            messagebox.showerror(
                "Permission Denied",
                "Only Admin and Super Admin can clear threshold history."
            )
            return
        
        filter_type = self.filter_var.get()
        
        response = messagebox.askyesno(
            "Confirm Clear",
            f"Are you sure you want to clear all {filter_type} threshold history?\n\n"
            "This action cannot be undone."
        )
        
        if response:
            if self.db.clear_threshold_history(filter_type):
                messagebox.showinfo("Success", f"{filter_type} threshold history cleared successfully!")
                self.load_history()
            else:
                messagebox.showerror("Error", "Failed to clear threshold history!")

