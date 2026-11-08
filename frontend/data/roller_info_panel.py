"""
Roller Information Panel
CRUD operations for individual roller configurations
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts
from ..utils.debug_logger import log_error, log_warning, log_info
from .data_database import DataDatabase


class RollerInfoPanel:
    """Panel for managing individual roller information."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the roller info panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        self.db = DataDatabase()
        
        self.entries = {}
        
        self.selected_roller_id = None
        
        self.create_btn = None
        self.read_btn = None
        self.update_btn = None
        self.delete_btn = None
        
    def create(self):
        """Create the roller info panel UI."""
        main_frame = tk.LabelFrame(
            self.parent,
            text="Roller Information",
            font=("Arial", 12, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        fields_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        fields_frame.pack(fill=tk.X, padx=15, pady=(10, 10))
        
        fields = [
            ("Roller Type", "roller_type"),
            ("Outer Diameter (mm)", "outer_diameter"),
            ("Dimple Diameter (mm)", "dimple_diameter"),
            ("Small Diameter (mm)", "small_diameter"),
            ("Length (mm)", "length_mm"),
            ("High Head (pixels)", "high_head_pixels"),
            ("Down Head (pixels)", "down_head_pixels")
        ]
        
        for idx, (label_text, field_name) in enumerate(fields):
            field_container = tk.Frame(fields_frame, bg=Colors.PRIMARY_BG)
            field_container.grid(row=0, column=idx, padx=5, pady=5, sticky="ew")
            
            label = tk.Label(
                field_container,
                text=label_text,
                font=Fonts.SMALL,
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG
            )
            label.pack(anchor="w")
            
            entry = tk.Entry(
                field_container,
                font=Fonts.TEXT,
                bg=Colors.WHITE,
                fg="#000000",
                insertbackground="#000000"
            )
            entry.pack(fill=tk.X)
            
            self.entries[field_name] = entry
        
        for i in range(7):
            fields_frame.grid_columnconfigure(i, weight=1)
        
        button_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.create_btn = tk.Button(
            button_frame,
            text="Create",
            font=Fonts.TEXT_BOLD,
            bg="#28A745",
            fg=Colors.WHITE,
            command=self.create_roller,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.create_btn.pack(side=tk.LEFT, padx=5)
        
        self.read_btn = tk.Button(
            button_frame,
            text="Read",
            font=Fonts.TEXT_BOLD,
            bg="#007BFF",
            fg=Colors.WHITE,
            command=self.read_roller,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.read_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = tk.Button(
            button_frame,
            text="Update",
            font=Fonts.TEXT_BOLD,
            bg="#FFC107",
            fg="#000000",
            command=self.update_roller,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = tk.Button(
            button_frame,
            text="Delete",
            font=Fonts.TEXT_BOLD,
            bg="#DC3545",
            fg=Colors.WHITE,
            command=self.delete_roller,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)
    
    def create_roller(self):
        """Create a new roller entry."""
        try:
            values = {}
            for field_name, entry in self.entries.items():
                value = entry.get().strip()
                if not value:
                    messagebox.showerror("Validation Error", 
                                       f"Please fill in all fields.\n\n{field_name} is empty.")
                    return
                
                if field_name != 'roller_type':
                    try:
                        if field_name in ['high_head_pixels', 'down_head_pixels']:
                            values[field_name] = int(value)
                        else:
                            values[field_name] = float(value)
                    except ValueError:
                        messagebox.showerror("Validation Error", 
                                           f"Invalid value for {field_name}.\n\nPlease enter a valid number.")
                        return
                else:
                    values[field_name] = value
            
            if self.db.roller_type_exists(values['roller_type']):
                messagebox.showerror("Validation Error", 
                                   f"Roller type '{values['roller_type']}' already exists.\n\n"
                                   "Please use a unique name.")
                return
            
            global_limits = self.db.get_global_limits()
            if global_limits:
                validation_errors = []
                
                if not (global_limits['min_outer_diameter'] <= values['outer_diameter'] <= global_limits['max_outer_diameter']):
                    validation_errors.append(f"Outer Diameter must be between {global_limits['min_outer_diameter']} and {global_limits['max_outer_diameter']}")
                
                if not (global_limits['min_dimple_diameter'] <= values['dimple_diameter'] <= global_limits['max_dimple_diameter']):
                    validation_errors.append(f"Dimple Diameter must be between {global_limits['min_dimple_diameter']} and {global_limits['max_dimple_diameter']}")
                
                if not (global_limits['min_small_diameter'] <= values['small_diameter'] <= global_limits['max_small_diameter']):
                    validation_errors.append(f"Small Diameter must be between {global_limits['min_small_diameter']} and {global_limits['max_small_diameter']}")
                
                if not (global_limits['min_length'] <= values['length_mm'] <= global_limits['max_length']):
                    validation_errors.append(f"Length must be between {global_limits['min_length']} and {global_limits['max_length']}")
                
                if validation_errors:
                    messagebox.showerror("Validation Error", 
                                       "Values exceed global limits:\n\n" + "\n".join(validation_errors))
                    return
            else:
                messagebox.showwarning("Warning", 
                                     "No global limits set. Please set global limits first for validation.")
                return
            
            created_by = self.app.current_user if hasattr(self.app, 'current_user') else 'system'
            
            success = self.db.create_roller(values, created_by)
            
            if success:
                messagebox.showinfo("Success", f"Roller '{values['roller_type']}' created successfully!")
                self.clear_fields()
                if hasattr(self.app, 'data_tab') and self.app.data_tab and self.app.data_tab.roller_data_table:
                    self.app.data_tab.roller_data_table.load_roller_data()
                self.app.roller_data_updated = True
            else:
                messagebox.showerror("Error", "Failed to create roller.")
        
        except Exception as e:
            print(f"❌ Error creating roller: {e}")
            messagebox.showerror("Error", f"Failed to create roller:\n{str(e)}")
    
    def read_roller(self):
        """Read/Load selected roller from table."""
        if hasattr(self.app, 'data_tab') and self.app.data_tab and self.app.data_tab.roller_data_table:
            selected = self.app.data_tab.roller_data_table.get_selected_roller()
            if selected:
                self.load_roller_data(selected)
            else:
                messagebox.showwarning("No Selection", "Please select a roller from the table below.")
        else:
            messagebox.showwarning("Error", "Roller data table not available.")
    
    def load_roller_data(self, roller_data):
        """Load roller data into form fields."""
        self.selected_roller_id = roller_data['id']
        
        self.entries['roller_type'].delete(0, tk.END)
        self.entries['roller_type'].insert(0, roller_data['roller_type'])
        
        self.entries['outer_diameter'].delete(0, tk.END)
        self.entries['outer_diameter'].insert(0, str(roller_data['outer_diameter']))
        
        self.entries['dimple_diameter'].delete(0, tk.END)
        self.entries['dimple_diameter'].insert(0, str(roller_data['dimple_diameter']))
        
        self.entries['small_diameter'].delete(0, tk.END)
        self.entries['small_diameter'].insert(0, str(roller_data['small_diameter']))
        
        self.entries['length_mm'].delete(0, tk.END)
        self.entries['length_mm'].insert(0, str(roller_data['length_mm']))
        
        self.entries['high_head_pixels'].delete(0, tk.END)
        self.entries['high_head_pixels'].insert(0, str(roller_data['high_head_pixels']))
        
        self.entries['down_head_pixels'].delete(0, tk.END)
        self.entries['down_head_pixels'].insert(0, str(roller_data['down_head_pixels']))
    
    def update_roller(self):
        """Update the selected roller."""
        try:
            log_info("data", f"Attempting to update roller (ID: {self.selected_roller_id})")
            
            if not self.selected_roller_id:
                log_warning("data", "Update roller failed: No roller selected")
                messagebox.showwarning("No Selection", 
                                     "Please select a roller using the 'Read' button first.")
                return
            
            values = {}
            for field_name, entry in self.entries.items():
                value = entry.get().strip()
                if not value:
                    log_warning("data", f"Update roller validation failed: {field_name} is empty")
                    messagebox.showerror("Validation Error", 
                                       f"Please fill in all fields.\n\n{field_name} is empty.")
                    return
                
                if field_name != 'roller_type':
                    try:
                        if field_name in ['high_head_pixels', 'down_head_pixels']:
                            values[field_name] = int(value)
                        else:
                            values[field_name] = float(value)
                    except ValueError:
                        log_warning("data", f"Update roller validation failed: Invalid value for {field_name} = {value}")
                        messagebox.showerror("Validation Error", 
                                           f"Invalid value for {field_name}.\n\nPlease enter a valid number.")
                        return
                else:
                    values[field_name] = value
            
            if self.db.roller_type_exists(values['roller_type'], exclude_id=self.selected_roller_id):
                log_warning("data", f"Update roller failed: Roller type '{values['roller_type']}' already exists")
                messagebox.showerror("Validation Error", 
                                   f"Roller type '{values['roller_type']}' already exists.\n\n"
                                   "Please use a unique name.")
                return
            
            global_limits = self.db.get_global_limits()
            if global_limits:
                validation_errors = []
                
                if not (global_limits['min_outer_diameter'] <= values['outer_diameter'] <= global_limits['max_outer_diameter']):
                    validation_errors.append(f"Outer Diameter must be between {global_limits['min_outer_diameter']} and {global_limits['max_outer_diameter']}")
                
                if not (global_limits['min_dimple_diameter'] <= values['dimple_diameter'] <= global_limits['max_dimple_diameter']):
                    validation_errors.append(f"Dimple Diameter must be between {global_limits['min_dimple_diameter']} and {global_limits['max_dimple_diameter']}")
                
                if not (global_limits['min_small_diameter'] <= values['small_diameter'] <= global_limits['max_small_diameter']):
                    validation_errors.append(f"Small Diameter must be between {global_limits['min_small_diameter']} and {global_limits['max_small_diameter']}")
                
                if not (global_limits['min_length'] <= values['length_mm'] <= global_limits['max_length']):
                    validation_errors.append(f"Length must be between {global_limits['min_length']} and {global_limits['max_length']}")
                
                if validation_errors:
                    log_warning("data", f"Update roller validation failed: Values exceed global limits - {validation_errors}")
                    messagebox.showerror("Validation Error", 
                                       "Values exceed global limits:\n\n" + "\n".join(validation_errors))
                    return
            
            success = self.db.update_roller(self.selected_roller_id, values)
            
            if success:
                log_info("data", f"Roller '{values['roller_type']}' (ID: {self.selected_roller_id}) updated successfully")
                messagebox.showinfo("Success", f"Roller '{values['roller_type']}' updated successfully!")
                self.clear_fields()
                self.selected_roller_id = None
                if hasattr(self.app, 'data_tab') and self.app.data_tab and self.app.data_tab.roller_data_table:
                    self.app.data_tab.roller_data_table.load_roller_data()
                self.app.roller_data_updated = True
            else:
                log_error("data", f"Failed to update roller '{values['roller_type']}' (ID: {self.selected_roller_id}) - Database operation returned False")
                messagebox.showerror("Error", "Failed to update roller.")
        
        except Exception as e:
            log_error("data", f"Error updating roller (ID: {self.selected_roller_id})", e)
            print(f"❌ Error updating roller: {e}")
            messagebox.showerror("Error", f"Failed to update roller:\n{str(e)}")
    
    def delete_roller(self):
        """Delete the selected roller."""
        try:
            log_info("data", f"Attempting to delete roller (ID: {self.selected_roller_id})")
            
            if not self.selected_roller_id:
                log_warning("data", "Delete roller failed: No roller selected")
                messagebox.showwarning("No Selection", 
                                     "Please select a roller using the 'Read' button first.")
                return
            
            roller_type = self.entries['roller_type'].get().strip()
            response = messagebox.askyesno("Confirm Deletion", 
                                          f"Are you sure you want to delete roller '{roller_type}'?\n\n"
                                          "This action cannot be undone.")
            
            if not response:
                log_info("data", f"Roller deletion cancelled by user for '{roller_type}' (ID: {self.selected_roller_id})")
                return
            
            success = self.db.delete_roller(self.selected_roller_id)
            
            if success:
                log_info("data", f"Roller '{roller_type}' (ID: {self.selected_roller_id}) deleted successfully")
                messagebox.showinfo("Success", f"Roller '{roller_type}' deleted successfully!")
                self.clear_fields()
                self.selected_roller_id = None
                if hasattr(self.app, 'data_tab') and self.app.data_tab and self.app.data_tab.roller_data_table:
                    self.app.data_tab.roller_data_table.load_roller_data()
                self.app.roller_data_updated = True
            else:
                log_error("data", f"Failed to delete roller '{roller_type}' (ID: {self.selected_roller_id}) - Database operation returned False")
                messagebox.showerror("Error", "Failed to delete roller.")
        
        except Exception as e:
            log_error("data", f"Error deleting roller (ID: {self.selected_roller_id})", e)
            print(f"❌ Error deleting roller: {e}")
            messagebox.showerror("Error", f"Failed to delete roller:\n{str(e)}")
    
    def clear_fields(self):
        """Clear all input fields."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.selected_roller_id = None
