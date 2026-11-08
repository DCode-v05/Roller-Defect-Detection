"""
Info Database Operations
Handles database operations for application settings, history, and system info
"""

import mysql.connector
from datetime import datetime
from ..utils.config import AppConfig
from ..utils.db_error_handler import DatabaseErrorHandler


class InfoDatabase:
    """Database handler for info tab operations."""
    
    def __init__(self, host=None, user=None, password=None, database=None):
        """
        Initialize database connection.
        
        Args:
            host: MySQL server host (defaults to AppConfig.DB_HOST)
            user: Database username (defaults to AppConfig.DB_USER)
            password: Database password (defaults to AppConfig.DB_PASSWORD)
            database: Database name (defaults to AppConfig.DB_DATABASE)
        """
        self.host = host or AppConfig.DB_HOST
        self.user = user or AppConfig.DB_USER
        self.password = password or AppConfig.DB_PASSWORD
        self.database = database or AppConfig.DB_DATABASE
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
        except Exception as e:
            print(f"❌ Error connecting to MySQL database: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="database connection")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def get_app_title(self):
        """
        Get current application title from database.
        
        Returns:
            str: Application title or default "WELVISION"
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return "WELVISION"
            
            if not self.connection:
                return "WELVISION"
            
            cursor = self.connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_by VARCHAR(100)
                )
            """)
            
            cursor.execute("SELECT setting_value FROM app_settings WHERE setting_key = 'app_title'")
            result = cursor.fetchone()
            
            cursor.close()
            
            if result:
                return result[0]
            else:
                return "WELVISION"
        
        except Exception as e:
            print(f"❌ Error getting app title: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="getting app title")
            return "WELVISION"
    
    def update_app_title(self, new_title, updated_by):
        """
        Update application title in database.
        
        Args:
            new_title: New application title
            updated_by: User who updated the title
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
            
            if not self.connection:
                return False
            
            cursor = self.connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_by VARCHAR(100)
                )
            """)
            
            cursor.execute("""
                INSERT INTO app_settings (setting_key, setting_value, updated_by)
                VALUES ('app_title', %s, %s)
                ON DUPLICATE KEY UPDATE 
                    setting_value = VALUES(setting_value),
                    updated_by = VALUES(updated_by),
                    updated_at = CURRENT_TIMESTAMP
            """, (new_title, updated_by))
            
            self.connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            print(f"❌ Error updating app title: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="updating app title")
            return False
    
    def get_threshold_history(self, filter_type='Overall', from_date=None, to_date=None):
        """
        Get threshold history from BF and/or OD threshold tables.
        
        Args:
            filter_type: 'BF', 'OD', or 'Overall'
            from_date: Start date for filtering
            to_date: End date for filtering
            
        Returns:
            list: List of threshold history records
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            if not self.connection:
                return []
            
            cursor = self.connection.cursor()
            
            results = []
            
            if filter_type in ['BF', 'Overall']:
                query = """
                    SELECT id, 'BF' as type, model_name, employee_id, change_timestamp, 
                           defect_threshold, size_threshold, model_threshold
                    FROM bf_threshold_history
                    WHERE DATE(change_timestamp) BETWEEN %s AND %s
                    ORDER BY change_timestamp DESC
                """
                cursor.execute(query, (from_date, to_date))
                bf_results = cursor.fetchall()
                results.extend(bf_results)
            
            if filter_type in ['OD', 'Overall']:
                query = """
                    SELECT id, 'OD' as type, model_name, employee_id, change_timestamp, 
                           defect_threshold, size_threshold, model_threshold
                    FROM od_threshold_history
                    WHERE DATE(change_timestamp) BETWEEN %s AND %s
                    ORDER BY change_timestamp DESC
                """
                cursor.execute(query, (from_date, to_date))
                od_results = cursor.fetchall()
                results.extend(od_results)
            
            cursor.close()
            
            results.sort(key=lambda x: x[4], reverse=True)
            
            return results
        
        except Exception as e:
            print(f"❌ Error getting threshold history: {e}")
            import traceback
            traceback.print_exc()
            DatabaseErrorHandler.handle_db_error(e, context="getting threshold history")
            return []
    
    def clear_threshold_history(self, filter_type='Overall'):
        """
        Clear threshold history for specified type.
        
        Args:
            filter_type: 'BF', 'OD', or 'Overall'
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
            
            if not self.connection:
                return False
            
            cursor = self.connection.cursor()
            
            if filter_type in ['BF', 'Overall']:
                cursor.execute("DELETE FROM bf_threshold_history")
            
            if filter_type in ['OD', 'Overall']:
                cursor.execute("DELETE FROM od_threshold_history")
            
            self.connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            print(f"❌ Error clearing threshold history: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="clearing threshold history")
            return False
