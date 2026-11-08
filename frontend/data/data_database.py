"""
Database operations for Data Management
Handles global limits and roller data CRUD operations
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime

from frontend.utils.config import AppConfig
from ..utils.db_error_handler import DatabaseErrorHandler


class DataDatabase:
    """Database handler for roller data management."""

    def __init__(self):
        """
        Initialize database connection.
        """
        self.host = AppConfig.DB_HOST
        self.port = AppConfig.DB_PORT
        self.user = AppConfig.DB_USER
        self.password = AppConfig.DB_PASSWORD
        self.database = AppConfig.DB_DATABASE
        self.connection = None
    
    def _get_connection(self):
        """Get a database connection."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"❌ Error connecting to MySQL database: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="database connection")
            return None
    
    def save_global_limits(self, limits, updated_by):
        """
        Save or update global roller limits.
        
        Args:
            limits: Dictionary containing limit values
            updated_by: User who is updating the limits
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = self._get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM global_roller_limits")
            count = cursor.fetchone()[0]
            
            if count > 0:
                update_query = """
                UPDATE global_roller_limits 
                SET min_outer_diameter = %s,
                    max_outer_diameter = %s,
                    min_dimple_diameter = %s,
                    max_dimple_diameter = %s,
                    min_small_diameter = %s,
                    max_small_diameter = %s,
                    min_length = %s,
                    max_length = %s,
                    updated_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
                """
                
                data = (
                    limits['min_outer_diameter'],
                    limits['max_outer_diameter'],
                    limits['min_dimple_diameter'],
                    limits['max_dimple_diameter'],
                    limits['min_small_diameter'],
                    limits['max_small_diameter'],
                    limits['min_length'],
                    limits['max_length'],
                    updated_by
                )
            else:
                insert_query = """
                INSERT INTO global_roller_limits 
                (min_outer_diameter, max_outer_diameter, min_dimple_diameter, 
                 max_dimple_diameter, min_small_diameter, max_small_diameter, 
                 min_length, max_length, updated_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                data = (
                    limits['min_outer_diameter'],
                    limits['max_outer_diameter'],
                    limits['min_dimple_diameter'],
                    limits['max_dimple_diameter'],
                    limits['min_small_diameter'],
                    limits['max_small_diameter'],
                    limits['min_length'],
                    limits['max_length'],
                    updated_by
                )
            
            cursor.execute(update_query if count > 0 else insert_query, data)
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
        
        except Error as e:
            print(f"❌ Error saving global limits: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="saving global limits")
            return False
    
    def get_global_limits(self):
        """
        Get current global roller limits.
        
        Returns:
            dict: Dictionary containing limit values, or None if not found
        """
        try:
            connection = self._get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT min_outer_diameter, max_outer_diameter,
                   min_dimple_diameter, max_dimple_diameter,
                   min_small_diameter, max_small_diameter,
                   min_length, max_length
            FROM global_roller_limits
            LIMIT 1
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return result
        
        except Error as e:
            print(f"❌ Error getting global limits: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="getting global limits")
            return None
    
    def create_roller(self, roller_data, created_by):
        """
        Create a new roller entry.
        
        Args:
            roller_data: Dictionary containing roller information
            created_by: User creating the roller
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = self._get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            insert_query = """
            INSERT INTO roller_data 
            (roller_type, outer_diameter, dimple_diameter, small_diameter, 
             length_mm, high_head_pixels, down_head_pixels, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            data = (
                roller_data['roller_type'],
                roller_data['outer_diameter'],
                roller_data['dimple_diameter'],
                roller_data['small_diameter'],
                roller_data['length_mm'],
                roller_data['high_head_pixels'],
                roller_data['down_head_pixels'],
                created_by
            )
            
            cursor.execute(insert_query, data)
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
        
        except Error as e:
            print(f"❌ Error creating roller: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="creating roller")
            return False
    
    def get_all_rollers(self):
        """
        Get all roller data.
        
        Returns:
            list: List of roller dictionaries
        """
        try:
            connection = self._get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT id, roller_type, outer_diameter, dimple_diameter, 
                   small_diameter, length_mm, high_head_pixels, down_head_pixels
            FROM roller_data
            ORDER BY id DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return results
        
        except Error as e:
            print(f"❌ Error getting all rollers: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="getting all rollers")
            return []
    
    def update_roller(self, roller_id, roller_data):
        """
        Update an existing roller entry.
        
        Args:
            roller_id: ID of the roller to update
            roller_data: Dictionary containing updated roller information
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = self._get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            update_query = """
            UPDATE roller_data 
            SET roller_type = %s,
                outer_diameter = %s,
                dimple_diameter = %s,
                small_diameter = %s,
                length_mm = %s,
                high_head_pixels = %s,
                down_head_pixels = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            
            data = (
                roller_data['roller_type'],
                roller_data['outer_diameter'],
                roller_data['dimple_diameter'],
                roller_data['small_diameter'],
                roller_data['length_mm'],
                roller_data['high_head_pixels'],
                roller_data['down_head_pixels'],
                roller_id
            )
            
            cursor.execute(update_query, data)
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
        
        except Error as e:
            print(f"❌ Error updating roller: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="updating roller")
            return False
    
    def delete_roller(self, roller_id):
        """
        Delete a roller entry.
        
        Args:
            roller_id: ID of the roller to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            connection = self._get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            delete_query = "DELETE FROM roller_data WHERE id = %s"
            
            cursor.execute(delete_query, (roller_id,))
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
        
        except Error as e:
            print(f"❌ Error deleting roller: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="deleting roller")
            return False
    
    def roller_type_exists(self, roller_type, exclude_id=None):
        """
        Check if a roller type already exists.
        
        Args:
            roller_type: Roller type name to check
            exclude_id: ID to exclude from check (for updates)
        
        Returns:
            bool: True if exists, False otherwise
        """
        try:
            connection = self._get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            if exclude_id:
                query = "SELECT COUNT(*) FROM roller_data WHERE roller_type = %s AND id != %s"
                cursor.execute(query, (roller_type, exclude_id))
            else:
                query = "SELECT COUNT(*) FROM roller_data WHERE roller_type = %s"
                cursor.execute(query, (roller_type,))
            
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return count > 0
        
        except Error as e:
            print(f"❌ Error checking roller type existence: {e}")
            DatabaseErrorHandler.handle_db_error(e, context="checking roller type existence")
            return False
