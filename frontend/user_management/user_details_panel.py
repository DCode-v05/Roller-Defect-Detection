"""
User Details Panel
Shows and edits details of selected user with dynamic form display
"""

import tkinter as tk
from tkinter import ttk
from ..utils.styles import Colors, Fonts
from ..utils.permissions import Permissions


class UserDetailsPanel:
    """Panel for displaying and editing user details with dynamic form."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize user details panel.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to UserManagementTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        
        self.employee_id_var = None
        self.email_var = None
        self.role_var = None
        self.status_var = None
        self.new_password_var = None
        self.confirm_password_var = None
        
        self.employee_id_entry = None
        self.email_entry = None
        self.role_combo = None
        self.active_radio = None
        self.inactive_radio = None
        self.new_password_entry = None
        self.confirm_password_entry = None
        
        self.main_frame = None
        self.details_frame = None
        self.user_info_frame = None
        self.password_frame = None
        self.save_button = None
        
        self.current_user_id = None
        self.original_data = {}
        
        self.form_mode = 'hidden'
    
    def create(self):
        """Create the user details panel UI."""
        self.main_frame = tk.LabelFrame(
            self.parent,
            text="👤 User Details",
            font=("Arial", 13, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.employee_id_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.role_var = tk.StringVar()
        self.status_var = tk.IntVar(value=1)
        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
        self.employee_id_var.trace('w', self._on_field_change)
        self.email_var.trace('w', self._on_field_change)
        self.role_var.trace('w', self._on_field_change)
        self.status_var.trace('w', self._on_field_change)
    
    def show_add_form(self):
        """Show form for adding new user."""
        self.form_mode = 'add'
        self._destroy_all_forms()
        self._create_user_info_form()
        self._create_password_form()
        self._create_save_button("Save User")
        self.clear()
    
    def show_read_form(self, user_data):
        """Show form for reading user details (read-only)."""
        self.form_mode = 'read'
        self._destroy_all_forms()
        self._create_user_info_form(readonly=True)
        self.populate(user_data)
    
    def show_update_form(self, user_data):
        """Show form for updating user (no password fields)."""
        self.form_mode = 'update'
        self.original_data = user_data.copy()
        self._destroy_all_forms()
        self._create_user_info_form(readonly=False)
        self.populate(user_data)
    
    def show_password_form(self, user_data):
        """Show form for changing password only."""
        self.form_mode = 'change_password'
        self._destroy_all_forms()
        
        info_frame = tk.Frame(self.main_frame, bg=Colors.PRIMARY_BG)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            info_frame,
            text=f"Employee ID: {user_data.get('employee_id', '')}",
            font=("Arial", 11, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(anchor=tk.W)
        
        tk.Label(
            info_frame,
            text=f"Email: {user_data.get('email', '')}",
            font=("Arial", 10),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(anchor=tk.W, pady=(5, 0))
        
        self._create_password_form()
        self._create_save_button("Update Password")
        self.current_user_id = user_data.get('id')
        
        self.current_password_hash = user_data.get('password_hash', '')
        self.current_salt = user_data.get('salt', '')
    
    def hide_form(self):
        """Hide the form and return to empty state."""
        self.form_mode = 'hidden'
        self._destroy_all_forms()
        self.clear()
    
    def _destroy_all_forms(self):
        """Destroy all form widgets."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.user_info_frame = None
        self.password_frame = None
        self.save_button = None
    
    def _create_user_info_form(self, readonly=False):
        """Create user information form."""
        self.user_info_frame = tk.Frame(self.main_frame, bg=Colors.PRIMARY_BG)
        self.user_info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._create_field(
            self.user_info_frame,
            "👤 Employee ID:",
            "employee_id",
            readonly
        )
        
        self._create_field(
            self.user_info_frame,
            "📧 Email Address:",
            "email",
            readonly
        )
        
        self._create_role_field(self.user_info_frame, readonly)
        
        self._create_status_section(self.user_info_frame, readonly)
    
    def _create_password_form(self):
        """Create password form."""
        self.password_frame = tk.LabelFrame(
            self.main_frame,
            text="🔐 Password",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=1,
            relief=tk.GROOVE
        )
        self.password_frame.pack(fill=tk.X, padx=10, pady=8)
        
        pwd_frame = tk.Frame(self.password_frame, bg=Colors.PRIMARY_BG)
        pwd_frame.pack(fill=tk.X, padx=10, pady=(5, 3))
        
        pwd_label = tk.Label(
            pwd_frame,
            text="New Password:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        pwd_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.new_password_entry = tk.Entry(
            pwd_frame,
            textvariable=self.new_password_var,
            font=("Arial", 10),
            bg=Colors.WHITE,
            fg=Colors.BLACK,
            show="*",
            width=30
        )
        self.new_password_entry.pack(fill=tk.X)
        
        confirm_frame = tk.Frame(self.password_frame, bg=Colors.PRIMARY_BG)
        confirm_frame.pack(fill=tk.X, padx=10, pady=(3, 5))
        
        confirm_label = tk.Label(
            confirm_frame,
            text="Confirm Password:",
            font=("Arial", 9),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        confirm_label.pack(anchor=tk.W, pady=(0, 2))
        
        self.confirm_password_entry = tk.Entry(
            confirm_frame,
            textvariable=self.confirm_password_var,
            font=("Arial", 10),
            bg=Colors.WHITE,
            fg=Colors.BLACK,
            show="*",
            width=30
        )
        self.confirm_password_entry.pack(fill=tk.X)
    
    def _create_save_button(self, text):
        """Create save button."""
        self.save_button = tk.Button(
            self.main_frame,
            text=text,
            font=("Arial", 11, "bold"),
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            cursor="hand2",
            pady=10,
            command=self._on_save
        )
        self.save_button.pack(fill=tk.X, padx=10, pady=10)
    
    def _create_field(self, parent, label_text, field_name, readonly=False):
        """Create a standard input field."""
        frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        label.pack(anchor=tk.W, pady=(0, 2))
        
        if field_name == "employee_id":
            var = self.employee_id_var
        elif field_name == "email":
            var = self.email_var
        else:
            var = tk.StringVar()
        
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=("Arial", 10),
            bg=Colors.WHITE if not readonly else "#E0E0E0",
            fg=Colors.BLACK,
            width=35,
            state='readonly' if readonly else 'normal'
        )
        entry.pack(fill=tk.X)
        
        if field_name == "employee_id":
            self.employee_id_entry = entry
        elif field_name == "email":
            self.email_entry = entry
    
    def _create_role_field(self, parent, readonly=False):
        """Create role selection dropdown."""
        frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        label = tk.Label(
            frame,
            text="🔑 Role:",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        label.pack(anchor=tk.W, pady=(0, 2))
        
        style = ttk.Style()
        style.configure("UserRole.TCombobox", fieldbackground=Colors.WHITE)
        
        current_user_role = getattr(self.tab.app, 'current_role', 'Operator')
        
        if Permissions.can_manage_super_admin(current_user_role):
            available_roles = ["Admin", "Super Admin", "Operator"]
        else:
            available_roles = ["Admin", "Operator"]
        
        state = "disabled" if readonly else "readonly"
        
        self.role_combo = ttk.Combobox(
            frame,
            textvariable=self.role_var,
            values=available_roles,
            state=state,
            font=("Arial", 10),
            style="UserRole.TCombobox",
            width=32
        )
        self.role_combo.pack(fill=tk.X)
    
    def _create_status_section(self, parent, readonly=False):
        """Create account status radio buttons."""
        frame = tk.LabelFrame(
            parent,
            text="🔘 Account Status",
            font=("Arial", 10, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=1,
            relief=tk.GROOVE
        )
        frame.pack(fill=tk.X, padx=10, pady=8)
        
        radio_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        radio_frame.pack(fill=tk.X, padx=10, pady=5)
        
        state = 'disabled' if readonly else 'normal'
        
        self.active_radio = tk.Radiobutton(
            radio_frame,
            text="Active",
            variable=self.status_var,
            value=1,
            font=("Arial", 10),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            selectcolor=Colors.SUCCESS,
            activebackground=Colors.PRIMARY_BG,
            activeforeground=Colors.WHITE,
            state=state
        )
        self.active_radio.pack(side=tk.LEFT, padx=8)
        
        self.inactive_radio = tk.Radiobutton(
            radio_frame,
            text="Inactive",
            variable=self.status_var,
            value=0,
            font=("Arial", 10),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            selectcolor=Colors.DANGER,
            activebackground=Colors.PRIMARY_BG,
            activeforeground=Colors.WHITE,
            state=state
        )
        self.inactive_radio.pack(side=tk.LEFT, padx=8)
    
    def _on_field_change(self, *args):
        """Handle field changes in update mode."""
        if self.form_mode == 'update':
            current_data = {
                'employee_id': self.employee_id_var.get().strip(),
                'email': self.email_var.get().strip(),
                'role': self.role_var.get(),
                'is_active': bool(self.status_var.get())
            }
            
            has_changes = (
                current_data['employee_id'] != self.original_data.get('employee_id', '') or
                current_data['email'] != self.original_data.get('email', '') or
                current_data['role'] != self.original_data.get('role', '') or
                current_data['is_active'] != self.original_data.get('is_active', True)
            )
            
            if has_changes and not self.save_button:
                self._create_save_button("Save Changes")
            elif not has_changes and self.save_button:
                self.save_button.destroy()
                self.save_button = None
    
    def _on_save(self):
        """Handle save button click."""
        if self.form_mode == 'add':
            self.tab.add_user()
        elif self.form_mode == 'update':
            self.tab.update_user()
        elif self.form_mode == 'change_password':
            self.tab.change_password()
    
    def populate(self, user_data):
        """Populate fields with user data."""
        if not user_data:
            self.clear()
            return
        
        self.current_user_id = user_data.get('id')
        self.employee_id_var.set(user_data.get('employee_id', ''))
        self.email_var.set(user_data.get('email', ''))
        self.role_var.set(user_data.get('role', ''))
        self.status_var.set(1 if user_data.get('is_active') else 0)
        
        self.new_password_var.set('')
        self.confirm_password_var.set('')
    
    def clear(self):
        """Clear all fields."""
        self.current_user_id = None
        self.original_data = {}
        self.employee_id_var.set('')
        self.email_var.set('')
        self.role_var.set('')
        self.status_var.set(1)
        self.new_password_var.set('')
        self.confirm_password_var.set('')
    
    def get_data(self):
        """Get current form data."""
        return {
            'user_id': self.current_user_id,
            'employee_id': self.employee_id_var.get().strip(),
            'email': self.email_var.get().strip(),
            'role': self.role_var.get(),
            'is_active': bool(self.status_var.get()),
            'new_password': self.new_password_var.get(),
            'confirm_password': self.confirm_password_var.get()
        }
