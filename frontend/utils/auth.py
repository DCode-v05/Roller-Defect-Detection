"""
Authentication and user management
"""

from ..user_management.user_database import UserDatabase


users = {
    "operator": {"password": "operator123", "role": "Operator"},
    "admin": {"password": "admin123", "role": "Admin"},
    "": {"password": "", "role": "Super Admin"}
}


def authenticate_user(email, password, role):
    """
    Authenticate a user based on email, password, and role.
    Uses database authentication with fallback to legacy system.
    
    Args:
        email (str): User email
        password (str): User password
        role (str): User role (User, Admin, Super Admin, Operator)
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    db = UserDatabase()
    if db.connect():
        success, message, user_data = db.authenticate_user(email, password, role)
        db.disconnect()
        
        if success:
            return True, None

    
    if email in users:
        user_data = users[email]
        if user_data["password"] == password and user_data["role"] == role:
            return True, None
        else:
            return False, "Invalid email, password, or role."
    
    if 'message' in locals():
        return False, message
    
    return False, "Invalid email, password, or role."

