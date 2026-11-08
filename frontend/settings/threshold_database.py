"""
Database operations for threshold history
"""

import mysql.connector
from datetime import datetime
from ..utils.config import AppConfig
from ..utils.db_error_handler import DatabaseErrorHandler


class ThresholdDatabase:
    """Handles database operations for threshold history."""
    
    def __init__(self, host=None, user=None, password=None, database=None):
        """
        Initialize database connection parameters.
        
        Args:
            host: MySQL server host (defaults to AppConfig.DB_HOST)
            user: Database username (defaults to AppConfig.DB_USER)
            password: Database password (defaults to AppConfig.DB_PASSWORD)
            database: Database name (defaults to AppConfig.DB_DATABASE)
        """
        self.host = host or AppConfig.DB_HOST
        self.port = AppConfig.DB_PORT
        self.user = user or AppConfig.DB_USER
        self.password = password or AppConfig.DB_PASSWORD
        self.database = database or AppConfig.DB_DATABASE
    
    def save_bf_thresholds(self, employee_id, defect_thresholds, size_thresholds, model_confidence, model_name):
        """
        Save BF threshold settings to database.
        
        Args:
            employee_id: Employee ID
            defect_thresholds: Dictionary of defect thresholds {defect_name: value}
            size_thresholds: Dictionary of size thresholds {defect_name: value}
            model_confidence: Model confidence threshold (0-1)
            model_name: Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            cursor = connection.cursor()
            
            defect_threshold_str = ", ".join([f"{k}:{v}%" for k, v in defect_thresholds.items()])
            
            size_threshold_str = ", ".join([f"{k}:{v}" for k, v in size_thresholds.items()])
            
            query = """
                INSERT INTO bf_threshold_history 
                (employee_id, defect_threshold, size_threshold, model_threshold, model_name)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (employee_id, defect_threshold_str, size_threshold_str, model_confidence, model_name))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Database error saving BF thresholds: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="saving BF thresholds")
            return False
        except Exception as e:
            print(f"❌ Error saving BF thresholds: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="saving BF thresholds")
            return False
    
    def save_od_thresholds(self, employee_id, defect_thresholds, size_thresholds, model_confidence, model_name):
        """
        Save OD threshold settings to database.
        
        Args:
            employee_id: Employee ID
            defect_thresholds: Dictionary of defect thresholds {defect_name: value}
            size_thresholds: Dictionary of size thresholds {defect_name: value}
            model_confidence: Model confidence threshold (0-1)
            model_name: Name of the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            cursor = connection.cursor()
            
            defect_threshold_str = ", ".join([f"{k}:{v}%" for k, v in defect_thresholds.items()])
            
            size_threshold_str = ", ".join([f"{k}:{v}" for k, v in size_thresholds.items()])
            
            query = """
                INSERT INTO od_threshold_history 
                (employee_id, defect_threshold, size_threshold, model_threshold, model_name)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (employee_id, defect_threshold_str, size_threshold_str, model_confidence, model_name))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Database error saving OD thresholds: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="saving OD thresholds")
            return False
        except Exception as e:
            print(f"❌ Error saving OD thresholds: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="saving OD thresholds")
            return False
