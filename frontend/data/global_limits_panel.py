"""
Global Roller Limits Panel
Super Admin only section for setting machine-wide roller limits
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts
from ..utils.permissions import Permissions
from ..utils.debug_logger import log_error, log_warning, log_info
from .data_database import DataDatabase


class GlobalLimitsPanel:
    """Panel for managing global roller limits (Super Admin only)."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the global limits panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        self.db = DataDatabase()
        
        self.entries = {}
        
        
    def create(self):
        """Create the global limits panel UI."""
        user_role = getattr(self.app, 'current_role', 'Operator')
        
        can_modify = Permissions.can_modify_global_roller_limits(user_role)
        
        access_text = "(Read-Write)" if can_modify else "(Read-Only)"
        title_text = f"🌐 Global Roller Limits {access_text}"
        
        main_frame = tk.LabelFrame(
            self.parent,
            text=title_text,
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        desc_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        desc_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        access_msg = "Set minimum and maximum limits for ALL roller types to ensure quality standards" if can_modify else "View minimum and maximum limits for ALL roller types"
        desc_label = tk.Label(
            desc_frame,
            text=access_msg,
            font=Fonts.TEXT,
            fg="#FFC107" if can_modify else "#17A2B8",
            bg=Colors.PRIMARY_BG
        )
        desc_label.pack()
        
        range_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        range_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        range_title = tk.Label(
            range_frame,
            text="Machine range:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        range_title.pack(side=tk.LEFT)

        
        refresh_btn = tk.Button(
            range_frame,
            text="🔄 Refresh",
            font=Fonts.SMALL,
            bg="#17A2B8",
            fg=Colors.WHITE,
            command=self.load_current_limits,
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=2
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        fields_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        fields_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        fields = [
            ("Min Outer Diameter (mm):", "min_outer_diameter", "#00CED1"),
            ("Min Dimple Diameter (mm):", "min_dimple_diameter", "#00CED1"),
            ("Min Small Diameter (mm):", "min_small_diameter", "#00CED1"),
            ("Min Length (mm):", "min_length", "#00CED1"),
            ("Max Outer Diameter (mm):", "max_outer_diameter", "#FF1493"),
            ("Max Dimple Diameter (mm):", "max_dimple_diameter", "#FF1493"),
            ("Max Small Diameter (mm):", "max_small_diameter", "#FF1493"),
            ("Max Length (mm):", "max_length", "#FF1493")
        ]
        
        for idx, (label_text, field_name, color) in enumerate(fields):
            row = idx // 4
            col = idx % 4
            
            field_container = tk.Frame(fields_frame, bg=Colors.PRIMARY_BG)
            field_container.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            label = tk.Label(
                field_container,
                text=label_text,
                font=Fonts.SMALL_BOLD,
                fg=color,
                bg=Colors.PRIMARY_BG
            )
            label.pack(anchor="w")
            
            entry = tk.Entry(
                field_container,
                font=Fonts.TEXT,
                bg=Colors.WHITE,
                fg="#000000",
                insertbackground="#000000",
                state='normal' if can_modify else 'readonly'
            )
            entry.pack(fill=tk.X)
            
            self.entries[field_name] = entry
        
        for i in range(4):
            fields_frame.grid_columnconfigure(i, weight=1)
        
        warning_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        warning_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        if can_modify:
            warning_text = "⚠ These limits will apply to ALL roller types. Admin users cannot create rollers outside these ranges."
            warning_color = "#FF6B6B"
        else:
            warning_text = "ℹ You have read-only access to these limits. Only Super Admin can modify them."
            warning_color = "#17A2B8"
        
        warning_label = tk.Label(
            warning_frame,
            text=warning_text,
            font=Fonts.SMALL,
            fg=warning_color,
            bg=Colors.PRIMARY_BG
        )
        warning_label.pack()
        
        button_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        if can_modify:
            save_btn = tk.Button(
                button_frame,
                text="💾 Save Machine range",
                font=Fonts.TEXT_BOLD,
                bg="#28A745",
                fg=Colors.WHITE,
                command=self.save_machine_range,
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=8
            )
            save_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = tk.Button(
            button_frame,
            text="📁 Load Current",
            font=Fonts.TEXT_BOLD,
            bg="#007BFF",
            fg=Colors.WHITE,
            command=self.load_current_limits,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        load_btn.pack(side=tk.LEFT, padx=5)
        
        if can_modify:
            clear_btn = tk.Button(
                button_frame,
                text="🗑 Clear Fields",
                font=Fonts.TEXT_BOLD,
                bg="#6C757D",
                fg=Colors.WHITE,
                command=self.clear_fields,
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=8
            )
            clear_btn.pack(side=tk.LEFT, padx=5)
    
    def save_machine_range(self):
        """Save machine range to database."""
        try:
            log_info("data", "Attempting to save global roller limits")
            
            values = {}
            for field_name, entry in self.entries.items():
                value = entry.get().strip()
                if not value:
                    log_warning("data", f"Save global limits validation failed: {field_name} is empty")
                    messagebox.showerror("Validation Error", 
                                       f"Please fill in all fields.\n\n{field_name} is empty.")
                    return
                
                try:
                    values[field_name] = float(value)
                except ValueError:
                    log_warning("data", f"Save global limits validation failed: Invalid value for {field_name} = {value}")
                    messagebox.showerror("Validation Error", 
                                       f"Invalid value for {field_name}.\n\nPlease enter a valid number.")
                    return
            
            validations = [
                ("min_outer_diameter", "max_outer_diameter", "Outer Diameter"),
                ("min_dimple_diameter", "max_dimple_diameter", "Dimple Diameter"),
                ("min_small_diameter", "max_small_diameter", "Small Diameter"),
                ("min_length", "max_length", "Length")
            ]
            
            for min_field, max_field, dimension_name in validations:
                if values[min_field] >= values[max_field]:
                    log_warning("data", f"Save global limits validation failed: {dimension_name} min >= max ({values[min_field]} >= {values[max_field]})")
                    messagebox.showerror("Validation Error", 
                                       f"{dimension_name}: Minimum value must be less than maximum value.")
                    return
            
            updated_by = self.app.current_user if hasattr(self.app, 'current_user') else 'system'
            
            success = self.db.save_global_limits(values, updated_by)
            
            if success:
                log_info("data", f"Global roller limits saved successfully by user '{updated_by}'")
                messagebox.showinfo("Success", "Global roller limits saved successfully!")
                self.load_current_limits()
            else:
                log_error("data", "Failed to save global limits - Database operation returned False")
                messagebox.showerror("Error", "Failed to save global limits to database.")
        
        except Exception as e:
            log_error("data", "Error saving global roller limits", e)
            print(f"❌ Error saving machine range: {e}")
            messagebox.showerror("Error", f"Failed to save machine range:\n{str(e)}")
    
    def load_current_limits(self):
        """Load current limits from database."""
        try:
            limits = self.db.get_global_limits()
            
            if limits:
                for field_name in ['min_outer_diameter', 'max_outer_diameter', 
                                  'min_dimple_diameter', 'max_dimple_diameter',
                                  'min_small_diameter', 'max_small_diameter',
                                  'min_length', 'max_length']:
                    if field_name in self.entries:
                        entry = self.entries[field_name]
                        state = entry.cget('state')
                        if state == 'readonly':
                            entry.config(state='normal')
                        
                        entry.delete(0, tk.END)
                        entry.insert(0, str(limits[field_name]))
                        
                        if state == 'readonly':
                            entry.config(state='readonly')
                
            else:
                messagebox.showwarning("No Data", "No global limits found in database.\n\nPlease set limits first.")
        
        except Exception as e:
            print(f"❌ Error loading current limits: {e}")
            messagebox.showerror("Error", f"Failed to load current limits:\n{str(e)}")
    
    def clear_fields(self):
        """Clear all input fields."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
    
    def get_current_limits(self):
        """Get current limits from database."""
        return self.db.get_global_limits()
