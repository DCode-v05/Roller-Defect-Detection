"""
Role-Based Access Control (RBAC) Module
Defines permissions for different user roles
"""


class Permissions:
    """Permission definitions for role-based access control."""
    
    ROLES = {
        "Operator": 1,
        "Admin": 2,
        "Super Admin": 3
    }
    
    @staticmethod
    def can_access_allow_all_images(role):
        """
        Check if user can access 'Allow All Images' checkbox.
        Only Super Admin can access this feature.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role == "Super Admin"
    
    @staticmethod
    def can_access_user_management_tab(role):
        """
        Check if user can access User Management tab.
        Only Admin and Super Admin can access this tab.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_manage_users(role):
        """
        Check if user can manage other users.
        Admin and Super Admin can manage users.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_access_model_management_tab(role):
        """
        Check if user can access Model Management tab.
        Only Admin and Super Admin can access this tab.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_manage_models(role):
        """
        Check if user can upload/delete models.
        Admin and Super Admin can manage models.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_modify_settings(role):
        """
        Check if user can modify system settings.
        Admin and Super Admin can modify settings.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_access_system_check_tab(role):
        """
        Check if user can access System Check tab.
        Only Admin and Super Admin can access this tab.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_access_backup_tab(role):
        """
        Check if user can access Backup tab.
        Only Admin and Super Admin can access this tab.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_start_stop_inspection(role):
        """
        Check if user can start/stop inspection.
        All roles can control inspection.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return True
    
    @staticmethod
    def can_reset_counters(role):
        """
        Check if user can reset inspection counters.
        Admin and Super Admin can reset counters.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role in ["Admin", "Super Admin"]
    
    @staticmethod
    def can_modify_global_roller_limits(role):
        """
        Check if user can modify global roller limits (Read-Write access).
        Only Super Admin has write access.
        Operators and Admins have read-only access.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has write permission, False otherwise (read-only)
        """
        return role == "Super Admin"
    
    @staticmethod
    def can_change_gui_title(role):
        """
        Check if user can change GUI application title.
        Only Super Admin can change the title.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role == "Super Admin"
    
    @staticmethod
    def can_manage_super_admin(role):
        """
        Check if user can add/modify Super Admin users.
        Only Super Admin can manage other Super Admin accounts.
        Admin cannot add or modify Super Admin.
        
        Args:
            role (str): User role
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        return role == "Super Admin"
    
    @staticmethod
    def get_role_level(role):
        """
        Get numeric level for a role.
        
        Args:
            role (str): User role
            
        Returns:
            int: Role level (higher is more privileged)
        """
        return Permissions.ROLES.get(role, 0)
    
    @staticmethod
    def has_minimum_role(user_role, required_role):
        """
        Check if user has at least the required role level.
        
        Args:
            user_role (str): User's current role
            required_role (str): Minimum required role
            
        Returns:
            bool: True if user meets requirement, False otherwise
        """
        user_level = Permissions.get_role_level(user_role)
        required_level = Permissions.get_role_level(required_role)
        return user_level >= required_level
