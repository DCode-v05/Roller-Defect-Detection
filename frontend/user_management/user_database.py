"""
User Database Module
Handles all database operations for user management
"""

import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
from datetime import datetime, timedelta
from frontend.utils.config import AppConfig
from ..utils.db_error_handler import DatabaseErrorHandler


class UserDatabase:
    """Database handler for user management operations."""

    def __init__(self, host=AppConfig.DB_HOST, user=AppConfig.DB_USER, password=AppConfig.DB_PASSWORD, database=AppConfig.DB_DATABASE):
        """
        Initialize database connection.
        
        Args:
            host: MySQL server host
            user: Database username
            password: Database password
            database: Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"❌ Error connecting to MySQL database: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="database connection")
            return False
        return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash password with salt using SHA-256.
        
        Args:
            password: Plain text password
            salt: Salt string (generated if not provided)
            
        Returns:
            tuple: (password_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_salt = (password + salt).encode('utf-8')
        password_hash = hashlib.sha256(password_salt).hexdigest()
        
        return password_hash, salt
    
    @staticmethod
    def verify_password(password, stored_hash, salt):
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            stored_hash: Stored password hash
            salt: Salt used for hashing
            
        Returns:
            bool: True if password matches, False otherwise
        """
        password_hash, _ = UserDatabase.hash_password(password, salt)
        return password_hash == stored_hash
    
    def get_all_users(self):
        """
        Retrieve all users from database.
        
        Returns:
            list: List of user dictionaries
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT id, employee_id, email, role, is_active, 
                   failed_attempts, locked_until, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
            """
            
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            
            for user in users:
                if user['locked_until']:
                    user['locked_until'] = user['locked_until'].strftime('%Y-%m-%d %H:%M:%S')
                if user['created_at']:
                    user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if user['updated_at']:
                    user['updated_at'] = user['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                user['status'] = 'Active' if user['is_active'] else 'Inactive'
            
            return users
            
        except Error as e:
            print(f"❌ Error fetching users: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="fetching users")
            return []
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User data or None
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT id, employee_id, email, role, is_active, password_hash, salt,
                   failed_attempts, locked_until, created_at, updated_at
            FROM users
            WHERE id = %s
            """
            
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                if user['locked_until']:
                    user['locked_until'] = user['locked_until'].strftime('%Y-%m-%d %H:%M:%S')
                if user['created_at']:
                    user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if user['updated_at']:
                    user['updated_at'] = user['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                user['status'] = 'Active' if user['is_active'] else 'Inactive'
            
            return user
            
        except Error as e:
            print(f"❌ Error fetching user: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="fetching user")
            return None
    
    def get_user_by_employee_id(self, employee_id):
        """
        Get user by employee ID.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            dict: User data or None
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT id, employee_id, email, role, is_active, 
                   failed_attempts, locked_until, created_at, updated_at
            FROM users
            WHERE employee_id = %s
            """
            
            cursor.execute(query, (employee_id,))
            user = cursor.fetchone()
            cursor.close()
            
            return user
            
        except Error as e:
            print(f"❌ Error fetching user by employee_id: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="fetching user by employee ID")
            return None
    
    def add_user(self, employee_id, email, password, role, is_active=True):
        """
        Add new user to database.
        
        Args:
            employee_id: Employee ID
            email: User email
            password: Plain text password
            role: User role (Admin, Super Admin, Operator)
            is_active: Account active status
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            check_query = "SELECT employee_id, email FROM users WHERE employee_id = %s OR email = %s"
            cursor.execute(check_query, (employee_id, email))
            existing = cursor.fetchone()
            
            if existing:
                cursor.close()
                if existing[0] == employee_id:
                    return False, f"Employee ID '{employee_id}' already exists"
                else:
                    return False, f"Email '{email}' already exists"
            
            password_hash, salt = self.hash_password(password)
            
            insert_query = """
            INSERT INTO users (employee_id, email, password_hash, salt, role, is_active, failed_attempts)
            VALUES (%s, %s, %s, %s, %s, %s, 0)
            """
            
            cursor.execute(insert_query, (employee_id, email, password_hash, salt, role, is_active))
            self.connection.commit()
            cursor.close()
            
            return True, "User added successfully"
            
        except Error as e:
            print(f"❌ Error adding user: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="adding user")
            return False, f"Database error: {str(e)}"
    
    def update_user(self, user_id, employee_id, email, role, is_active):
        """
        Update existing user.
        
        Args:
            user_id: User ID to update
            employee_id: New employee ID
            email: New email
            role: New role
            is_active: New active status
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            check_query = """
            SELECT id, employee_id, email FROM users 
            WHERE (employee_id = %s OR email = %s) AND id != %s
            """
            cursor.execute(check_query, (employee_id, email, user_id))
            existing = cursor.fetchone()
            
            if existing:
                cursor.close()
                if existing[1] == employee_id:
                    return False, f"Employee ID '{employee_id}' already exists for another user"
                else:
                    return False, f"Email '{email}' already exists for another user"
            
            update_query = """
            UPDATE users 
            SET employee_id = %s, email = %s, role = %s, is_active = %s
            WHERE id = %s
            """
            
            cursor.execute(update_query, (employee_id, email, role, is_active, user_id))
            self.connection.commit()
            cursor.close()
            
            return True, "User updated successfully"
            
        except Error as e:
            print(f"❌ Error updating user: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="updating user")
            return False, f"Database error: {str(e)}"
    
    def delete_user(self, user_id):
        """
        Delete user from database.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            delete_query = "DELETE FROM users WHERE id = %s"
            cursor.execute(delete_query, (user_id,))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                cursor.close()
                return True, "User deleted successfully"
            else:
                cursor.close()
                return False, "User not found"
            
        except Error as e:
            print(f"❌ Error deleting user: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="deleting user")
            return False, f"Database error: {str(e)}"
    
    def change_password(self, user_id, new_password):
        """
        Change user password.
        
        Args:
            user_id: User ID
            new_password: New plain text password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            password_hash, salt = self.hash_password(new_password)
            
            cursor = self.connection.cursor()
            
            update_query = """
            UPDATE users 
            SET password_hash = %s, salt = %s, failed_attempts = 0, locked_until = NULL
            WHERE id = %s
            """
            
            cursor.execute(update_query, (password_hash, salt, user_id))
            self.connection.commit()
            cursor.close()
            
            return True, "Password changed successfully"
            
        except Error as e:
            print(f"❌ Error changing password: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="changing password")
            return False, f"Database error: {str(e)}"
    
    def authenticate_user(self, email, password, role):
        """
        Authenticate user login.
        
        Args:
            email: User email
            password: Plain text password
            role: Selected role
            
        Returns:
            tuple: (success: bool, message: str, user_data: dict or None)
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT id, employee_id, email, password_hash, salt, role, 
                   is_active, failed_attempts, locked_until
            FROM users
            WHERE email = %s
            """
            
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                return False, "Invalid email or password", None
            
            if not user['is_active']:
                cursor.close()
                return False, "Account is inactive. Contact administrator.", None
            
            if user['locked_until']:
                if datetime.now() < user['locked_until']:
                    remaining_seconds = (user['locked_until'] - datetime.now()).seconds
                    if remaining_seconds < 60:
                        cursor.close()
                        return False, f"Account locked. Try again in {remaining_seconds} seconds.", None
                    else:
                        remaining_minutes = remaining_seconds // 60
                        cursor.close()
                        return False, f"Account locked. Try again in {remaining_minutes} minutes.", None
                else:
                    unlock_query = "UPDATE users SET locked_until = NULL, failed_attempts = 0 WHERE id = %s"
                    cursor.execute(unlock_query, (user['id'],))
                    self.connection.commit()
            
            if user['role'] != role:
                cursor.close()
                return False, "Invalid role selected", None
            
            if not self.verify_password(password, user['password_hash'], user['salt']):
                failed_attempts = user['failed_attempts'] + 1
                
                if failed_attempts >= 3:
                    locked_until = datetime.now() + timedelta(minutes=5)
                    update_query = """
                    UPDATE users 
                    SET failed_attempts = %s, locked_until = %s 
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (failed_attempts, locked_until, user['id']))
                    self.connection.commit()
                    cursor.close()
                    return False, "Too many failed attempts. Account locked for 5 minutes.", None
                else:
                    update_query = "UPDATE users SET failed_attempts = %s WHERE id = %s"
                    cursor.execute(update_query, (failed_attempts, user['id']))
                    self.connection.commit()
                    cursor.close()
                    return False, f"Invalid password. {3 - failed_attempts} attempts remaining.", None
            
            reset_query = "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = %s"
            cursor.execute(reset_query, (user['id'],))
            self.connection.commit()
            cursor.close()
            
            return True, "Login successful", {
                'employee_id': user['employee_id'],
                'email': user['email'],
                'role': user['role']
            }
            
        except Error as e:
            print(f"❌ Error authenticating user: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="authenticating user")
            return False, f"Database error: {str(e)}", None
    
    def search_users(self, search_term):
        """
        Search users by employee_id, email, or role.
        
        Args:
            search_term: Search string
            
        Returns:
            list: List of matching users
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT id, employee_id, email, role, is_active, 
                   failed_attempts, locked_until, created_at, updated_at
            FROM users
            WHERE employee_id LIKE %s OR email LIKE %s OR role LIKE %s
            ORDER BY created_at DESC
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            users = cursor.fetchall()
            cursor.close()
            
            for user in users:
                if user['locked_until']:
                    user['locked_until'] = user['locked_until'].strftime('%Y-%m-%d %H:%M:%S')
                if user['created_at']:
                    user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if user['updated_at']:
                    user['updated_at'] = user['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                user['status'] = 'Active' if user['is_active'] else 'Inactive'
            
            return users
            
        except Error as e:
            print(f"❌ Error searching users: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="searching users")
            return []
    
    def count_super_admins(self):
        """
        Count the number of Super Admin users in the system.
        
        Returns:
            int: Number of Super Admin users
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            query = "SELECT COUNT(*) FROM users WHERE role = 'Super Admin'"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else 0
            
        except Error as e:
            print(f"❌ Error counting Super Admin users: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="counting Super Admin users")
            return 0
