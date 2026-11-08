"""
User Management Tab - Main Controller
Handles user CRUD operations and UI coordination
"""

import tkinter as tk
from ..utils.styles import Colors, Fonts
from ..utils.permissions import Permissions
from ..utils.debug_logger import log_error, log_warning, log_info
from .users_table import UsersTable
from .user_details_panel import UserDetailsPanel
from .user_actions import UserActions
from .user_database import UserDatabase


class UserManagementTab:
    """User Management tab for managing user accounts."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the user management tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.users_table = None
        self.user_details_panel = None
        self.user_actions = None
        
        self.db = UserDatabase()
    
    def setup(self):
        """Setup the user management tab UI."""
        try:
            log_info("user_management", "Setting up User Management tab")
            
            main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
            main_container.pack(fill=tk.BOTH, expand=True)
            
            header_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
            header_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
            
            title_label = tk.Label(
                header_frame,
                text="👥 User Management System",
                font=("Arial", 24, "bold"),
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG
            )
            title_label.pack(side=tk.LEFT)
            
            subtitle_label = tk.Label(
                main_container,
                text="Manage user accounts, roles, and passwords",
                font=("Arial", 11),
                fg="#FFD700",
                bg=Colors.PRIMARY_BG
            )
            subtitle_label.pack(padx=20, pady=(2, 5))
            
            content_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 5))
            
            left_frame = tk.LabelFrame(
                content_frame,
                text="📋 User Accounts",
                font=("Arial", 13, "bold"),
                fg=Colors.WHITE,
                bg=Colors.PRIMARY_BG,
                bd=2,
                relief=tk.RIDGE
            )
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
            
            self.users_table = UsersTable(left_frame, self)
            self.users_table.create()
            
            right_frame = tk.Frame(content_frame, bg=Colors.PRIMARY_BG)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(8, 0))
            right_frame.config(width=400)
            right_frame.pack_propagate(False)
            
            self.user_details_panel = UserDetailsPanel(right_frame, self)
            self.user_details_panel.create()
            
            self.user_actions = UserActions(main_container, self)
            self.user_actions.create()
            
            log_info("user_management", "User Management tab setup completed successfully")
        except Exception as e:
            log_error("user_management", "Failed to setup User Management tab", e)
            raise
        self.refresh_users()
    
    def refresh_users(self):
        """Refresh the users table with latest data from database."""
        if self.users_table:
            self.users_table.load_users()
    
    def populate_user_details(self, user_data):
        """
        Populate user details panel with selected user data.
        This is called when a user is selected from the table.
        
        Args:
            user_data: Dictionary containing user information
        """
        pass
    
    def clear_form(self):
        """Clear the user details form."""
        if self.user_details_panel:
            self.user_details_panel.hide_form()
    
    def add_user(self):
        """Add a new user (called from button or internally from panel)."""
        try:
            log_info("user_management", "Attempting to add new user")
            
            if self.user_details_panel.form_mode != 'add':
                self.user_details_panel.show_add_form()
                return
            
            data = self.user_details_panel.get_data()
            log_info("user_management", f"Adding user with Employee ID: {data.get('employee_id', 'N/A')}, Role: {data.get('role', 'N/A')}")
            
            current_user_role = getattr(self.app, 'current_role', 'Operator')
            
            if data['role'] == "Super Admin" and not Permissions.can_manage_super_admin(current_user_role):
                log_warning("user_management", f"Admin user tried to add Super Admin account - Permission denied")
                self.user_actions.show_error(
                    "Permission Denied\n\n"
                    "Admin users cannot add Super Admin accounts.\n"
                    "Only Super Admin can create other Super Admin users."
                )
                return
            
            if data['role'] == "Super Admin":
                if self.db.connect():
                    super_admin_count = self.db.count_super_admins()
                    self.db.disconnect()
                    
                    if super_admin_count >= 1:
                        log_warning("user_management", f"Attempted to add second Super Admin - Only one allowed")
                        self.user_actions.show_error(
                            "Super Admin Limit Reached\n\n"
                            "Only one Super Admin account is allowed in the system.\n"
                            "A Super Admin account already exists."
                        )
                        return
            
            if not data['employee_id']:
                log_warning("user_management", "Add user validation failed: Employee ID is required")
                self.user_actions.show_error("Employee ID is required")
                return
            
            if not data['email']:
                log_warning("user_management", "Add user validation failed: Email is required")
                self.user_actions.show_error("Email is required")
                return
            
            if not self.user_actions.validate_email(data['email']):
                log_warning("user_management", f"Add user validation failed: Invalid email format - {data['email']}")
                self.user_actions.show_error("Invalid email format")
                return
            
            if not data['role']:
                log_warning("user_management", "Add user validation failed: Role is required")
                self.user_actions.show_error("Role is required")
                return
            
            if not data['new_password']:
                log_warning("user_management", "Add user validation failed: Password is required")
                self.user_actions.show_error("Password is required for new user")
                return
            
            if data['new_password'] != data['confirm_password']:
                log_warning("user_management", "Add user validation failed: Passwords do not match")
                self.user_actions.show_error("Passwords do not match")
                return
            
            is_valid, msg = self.user_actions.validate_password(data['new_password'])
            if not is_valid:
                log_warning("user_management", f"Add user validation failed: Weak password - {msg}")
                self.user_actions.show_error(msg)
                return
            
            if not self.user_actions.confirm_action(
                "Add User",
                f"Add new user with Employee ID: {data['employee_id']}?"
            ):
                log_info("user_management", f"Add user cancelled by user for Employee ID: {data['employee_id']}")
                return
            
            if self.db.connect():
                success, message = self.db.add_user(
                    data['employee_id'],
                    data['email'],
                    data['new_password'],
                    data['role'],
                    data['is_active']
                )
                self.db.disconnect()
                
                if success:
                    log_info("user_management", f"User added successfully - Employee ID: {data['employee_id']}, Role: {data['role']}")
                    self.user_actions.show_success(message)
                    self.refresh_users()
                    self.user_details_panel.hide_form()
                else:
                    log_error("user_management", f"Failed to add user - Employee ID: {data['employee_id']}, Message: {message}")
                    self.user_actions.show_error(message)
            else:
                log_error("user_management", "Failed to add user - Database connection failed")
                self.user_actions.show_error("Database connection failed")
                
        except Exception as e:
            log_error("user_management", "Error adding user", e)
            self.user_actions.show_error(f"Failed to add user:\n{str(e)}")
    
    def read_user(self):
        """Read/view selected user details."""
        selected_user = self.users_table.get_selected_user()
        
        if not selected_user:
            self.user_actions.show_warning("Please select a user from the table")
            return
        
        self.user_details_panel.show_read_form(selected_user)
    
    def update_user(self):
        """Update selected user."""
        try:
            if self.user_details_panel.form_mode != 'update':
                selected_user = self.users_table.get_selected_user()
                if not selected_user:
                    self.user_actions.show_warning("Please select a user from the table")
                    return
                self.user_details_panel.show_update_form(selected_user)
                return
            
            data = self.user_details_panel.get_data()
            log_info("user_management", f"Attempting to update user - ID: {data.get('user_id', 'N/A')}, Employee ID: {data.get('employee_id', 'N/A')}")
            
            if not data['user_id']:
                log_warning("user_management", "Update user failed: No user selected")
                self.user_actions.show_warning("Please select a user to update")
                return
            
            current_user_role = getattr(self.app, 'current_role', 'Operator')
            
            selected_user = self.users_table.get_selected_user()
            if selected_user:
                original_role = selected_user.get('role', '')
                
                if original_role == "Super Admin" and not Permissions.can_manage_super_admin(current_user_role):
                    log_warning("user_management", f"Admin user tried to modify Super Admin account - Permission denied")
                    self.user_actions.show_error(
                        "Permission Denied\n\n"
                        "Admin users cannot modify Super Admin accounts.\n"
                        "Only Super Admin can update other Super Admin users."
                    )
                    return
                
                if data['role'] == "Super Admin" and not Permissions.can_manage_super_admin(current_user_role):
                    log_warning("user_management", f"Admin user tried to promote user to Super Admin - Permission denied")
                    self.user_actions.show_error(
                        "Permission Denied\n\n"
                        "Admin users cannot promote users to Super Admin.\n"
                        "Only Super Admin can assign Super Admin role."
                    )
                    return
                
                if data['role'] == "Super Admin" and original_role != "Super Admin":
                    if self.db.connect():
                        super_admin_count = self.db.count_super_admins()
                        self.db.disconnect()
                        
                        if super_admin_count >= 1:
                            log_warning("user_management", f"Attempted to promote user to Super Admin - Only one allowed")
                            self.user_actions.show_error(
                                "Super Admin Limit Reached\n\n"
                                "Only one Super Admin account is allowed in the system.\n"
                                "A Super Admin account already exists."
                            )
                            return
            
            if not data['employee_id']:
                log_warning("user_management", "Update user validation failed: Employee ID is required")
                self.user_actions.show_error("Employee ID is required")
                return
            
            if not data['email']:
                log_warning("user_management", "Update user validation failed: Email is required")
                self.user_actions.show_error("Email is required")
                return
            
            if not self.user_actions.validate_email(data['email']):
                log_warning("user_management", f"Update user validation failed: Invalid email format - {data['email']}")
                self.user_actions.show_error("Invalid email format")
                return
            
            if not data['role']:
                log_warning("user_management", "Update user validation failed: Role is required")
                self.user_actions.show_error("Role is required")
                return
            
            if not self.user_actions.confirm_action(
                "Update User",
                f"Update user: {data['employee_id']}?"
            ):
                log_info("user_management", f"Update user cancelled by user for Employee ID: {data['employee_id']}")
                return
            
            if self.db.connect():
                success, message = self.db.update_user(
                    data['user_id'],
                    data['employee_id'],
                    data['email'],
                    data['role'],
                    data['is_active']
                )
                self.db.disconnect()
                
                if success:
                    log_info("user_management", f"User updated successfully - Employee ID: {data['employee_id']}, Role: {data['role']}")
                    self.user_actions.show_success(message)
                    self.refresh_users()
                else:
                    log_error("user_management", f"Failed to update user - Employee ID: {data['employee_id']}, Message: {message}")
                    self.user_actions.show_error(message)
            else:
                log_error("user_management", "Failed to update user - Database connection failed")
                self.user_actions.show_error("Database connection failed")
                
        except Exception as e:
            log_error("user_management", "Error updating user", e)
            self.user_actions.show_error(f"Failed to update user:\n{str(e)}")
    
    def delete_user(self):
        """Delete selected user."""
        try:
            data = self.user_details_panel.get_data()
            log_info("user_management", f"Attempting to delete user - ID: {data.get('user_id', 'N/A')}, Employee ID: {data.get('employee_id', 'N/A')}")
            
            if not data['user_id']:
                log_warning("user_management", "Delete user failed: No user selected")
                self.user_actions.show_warning("Please select a user to delete")
                return
            
            current_user_role = getattr(self.app, 'current_role', 'Operator')
            
            selected_user = self.users_table.get_selected_user()
            if selected_user and selected_user.get('role') == "Super Admin":
                if not Permissions.can_manage_super_admin(current_user_role):
                    log_warning("user_management", f"Admin user tried to delete Super Admin account - Permission denied")
                    self.user_actions.show_error(
                        "Permission Denied\n\n"
                        "Admin users cannot delete Super Admin accounts.\n"
                        "Only Super Admin can delete other Super Admin users."
                    )
                    return
            
            if data['email'] == self.app.current_user:
                log_warning("user_management", f"Attempted to delete currently logged-in user - {data['email']}")
                self.user_actions.show_error("Cannot delete currently logged-in user")
                return
            
            if not self.user_actions.confirm_action(
                "Delete User",
                f"Are you sure you want to delete user: {data['employee_id']}?\n\n"
                "This action cannot be undone!"
            ):
                log_info("user_management", f"Delete user cancelled by user for Employee ID: {data['employee_id']}")
                return
            
            if self.db.connect():
                success, message = self.db.delete_user(data['user_id'])
                self.db.disconnect()
                
                if success:
                    log_info("user_management", f"User deleted successfully - Employee ID: {data['employee_id']}")
                    self.user_actions.show_success(message)
                    self.refresh_users()
                    self.user_details_panel.hide_form()
                else:
                    log_error("user_management", f"Failed to delete user - Employee ID: {data['employee_id']}, Message: {message}")
                    self.user_actions.show_error(message)
            else:
                log_error("user_management", "Failed to delete user - Database connection failed")
                self.user_actions.show_error("Database connection failed")
                
        except Exception as e:
            log_error("user_management", "Error deleting user", e)
            self.user_actions.show_error(f"Failed to delete user:\n{str(e)}")
    
    def change_password(self):
        """Change password for selected user."""
        if self.user_details_panel.form_mode != 'change_password':
            selected_user = self.users_table.get_selected_user()
            if not selected_user:
                self.user_actions.show_warning("Please select a user to change password")
                return
            self.user_details_panel.show_password_form(selected_user)
            return
        
        data = self.user_details_panel.get_data()
        
        if not data['user_id']:
            self.user_actions.show_warning("Please select a user to change password")
            return
        
        if not data['new_password']:
            self.user_actions.show_error("New password is required")
            return
        
        if data['new_password'] != data['confirm_password']:
            self.user_actions.show_error("Passwords do not match")
            return
        
        if hasattr(self.user_details_panel, 'current_password_hash') and hasattr(self.user_details_panel, 'current_salt'):
            import hashlib
            new_password_salt = (data['new_password'] + self.user_details_panel.current_salt).encode('utf-8')
            new_password_hash = hashlib.sha256(new_password_salt).hexdigest()
            
            if new_password_hash == self.user_details_panel.current_password_hash:
                self.user_actions.show_error("New password cannot be the same as current password")
                return
        
        is_valid, msg = self.user_actions.validate_password(data['new_password'])
        if not is_valid:
            self.user_actions.show_error(msg)
            return
        
        if not self.user_actions.confirm_action(
            "Change Password",
            f"Change password for user: {data['employee_id']}?"
        ):
            return
        
        if self.db.connect():
            success, message = self.db.change_password(
                data['user_id'],
                data['new_password']
            )
            self.db.disconnect()
            
            if success:
                self.user_actions.show_success(message)
                self.user_details_panel.hide_form()
            else:
                self.user_actions.show_error(message)
        else:
            self.user_actions.show_error("Database connection failed")
