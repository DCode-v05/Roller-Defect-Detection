"""
Model Database Operations
Handles CRUD operations for model metadata in MySQL database
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
from ..utils.config import AppConfig
from ..utils.db_error_handler import DatabaseErrorHandler


class ModelDatabase:
    """Database handler for model management."""
    
    def __init__(self):
        """Initialize database connection parameters."""

        self.host = AppConfig.DB_HOST
        self.port = AppConfig.DB_PORT
        self.user = AppConfig.DB_USER
        self.password = AppConfig.DB_PASSWORD
        self.database = AppConfig.DB_DATABASE
        
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
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
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def insert_model(self, model_name, model_type, model_path, uploaded_by):
        """
        Insert a new model into the database.
        
        Args:
            model_name: Name of the model
            model_type: Type of model (BIGFACE or OD)
            model_path: Full path to the model file
            uploaded_by: Email of user who uploaded
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            table = "bf_models" if model_type == "BIGFACE" else "od_models"
            
            insert_query = f"""
            INSERT INTO {table} (model_name, model_path, uploaded_by)
            VALUES (%s, %s, %s)
            """
            
            data = (model_name, model_path, uploaded_by)
            
            cursor.execute(insert_query, data)
            self.connection.commit()
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ Error inserting model: {e}")
            import traceback
            traceback.print_exc()
            DatabaseErrorHandler.handle_db_error(e, context="inserting model")
            return False
    
    def get_all_models(self, filter_type=None):
        """
        Get all models from database.
        
        Args:
            filter_type: Optional filter by type (BIGFACE or OD)
            
        Returns:
            list: List of model dictionaries
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            models = []
            
            if filter_type == "BIGFACE":
                tables = [("bf_models", "BIGFACE")]
            elif filter_type == "OD":
                tables = [("od_models", "OD")]
            else:
                tables = [("bf_models", "BIGFACE"), ("od_models", "OD")]
            
            for table, model_type in tables:
                query = f"""
                SELECT id, model_name, model_path, upload_date, uploaded_by
                FROM {table}
                ORDER BY upload_date DESC
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                for result in results:
                    result['model_type'] = model_type
                    models.append(result)
            
            cursor.close()
            return models
            
        except Error as e:
            print(f"❌ Error retrieving models: {e}")
            import traceback
            traceback.print_exc()
            DatabaseErrorHandler.handle_db_error(e, context="retrieving models")
            return []
    
    def delete_model(self, model_id, model_type):
        """
        Delete a model from database.
        
        Args:
            model_id: ID of the model to delete
            model_type: Type of model (BIGFACE or OD)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            table = "bf_models" if model_type == "BIGFACE" else "od_models"
            
            delete_query = f"""
            DELETE FROM {table}
            WHERE id = %s
            """
            
            cursor.execute(delete_query, (model_id,))
            self.connection.commit()
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ Error deleting model: {e}")
            import traceback
            traceback.print_exc()
            DatabaseErrorHandler.handle_db_error(e, context="deleting model")
            return False
    
    def update_model_name(self, model_id, model_type, new_name):
        """
        Update model name in database.
        
        Args:
            model_id: ID of the model to update
            model_type: Type of model (BIGFACE or OD)
            new_name: New name for the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            table = "bf_models" if model_type == "BIGFACE" else "od_models"
            
            update_query = f"""
            UPDATE {table}
            SET model_name = %s
            WHERE id = %s
            """
            
            cursor.execute(update_query, (new_name, model_id))
            self.connection.commit()
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ Error updating model name: {e}")
            import traceback
            traceback.print_exc()
            DatabaseErrorHandler.handle_db_error(e, context="updating model name")
            return False
