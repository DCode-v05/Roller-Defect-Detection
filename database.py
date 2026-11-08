"""
Database Module for Roller Tracking
Handles MySQL database operations for BF and OD roller inspection data
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, time as dt_time
import traceback
from frontend.utils.config import AppConfig


class RollerDatabase:
    """Database handler for roller inspection tracking."""
    
    def __init__(self):
        """
        Initialize database connection.
        
        Args:
            host: MySQL server host
            user: Database username
            password: Database password
            database: Database name
        """
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
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"❌ Error connecting to MySQL database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def insert_bf_tracking(self, employee_id, start_time, shared_data):
        """
        Insert BF roller tracking data into database.
        
        Args:
            employee_id: Employee ID
            start_time: Start time of inspection
            shared_data: Dictionary containing inspection statistics
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            report_date = date.today()
            end_time = datetime.now().time()
            
            roller_type = roller_type = shared_data.get("selected_roller_type", "Small")
            total_inspected = shared_data.get("bf_inspected", 0)
            total_accepted = shared_data.get("bf_ok_rollers", 0)
            total_rejected = shared_data.get("bf_not_ok_rollers", 0)
            total_rust = shared_data.get("bf_rust", 0)
            total_dent = shared_data.get("bf_dent", 0)
            total_damage = shared_data.get("bf_damage", 0)
            total_high_head = shared_data.get("bf_high_head", 0)
            total_low_head = shared_data.get("bf_down_head", 0)
            others = shared_data.get("bf_others", 0)

            insert_query = """
            INSERT INTO bf_roller_tracking 
            (roller_type, employee_id, report_date, start_time, end_time, 
             total_inspected, total_accepted, total_rejected, 
             total_rust, total_dent, total_damage, 
             total_high_head, total_low_head, others)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            data = (
                roller_type, employee_id, report_date, start_time, end_time,
                total_inspected, total_accepted, total_rejected,
                total_rust, total_dent, total_damage,
                total_high_head, total_low_head, others
            )
            
            cursor.execute(insert_query, data)
            self.connection.commit()
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ Error inserting BF tracking data: {e}")
            traceback.print_exc()
            return False
    
    def insert_od_tracking(self, employee_id, start_time, shared_data):
        """
        Insert OD roller tracking data into database.
        
        Args:
            employee_id: Employee ID
            start_time: Start time of inspection
            shared_data: Dictionary containing inspection statistics
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            report_date = date.today()
            end_time = datetime.now().time()
            
            roller_type = roller_type = shared_data.get("selected_roller_type", "Small")
            total_inspected = shared_data.get("od_inspected", 0)
            total_accepted = shared_data.get("od_ok_rollers", 0)
            total_rejected = shared_data.get("od_not_ok_rollers", 0)
            total_rust = shared_data.get("od_rust", 0)
            total_dent = shared_data.get("od_dent", 0)
            total_damage = shared_data.get("od_damage", 0)
            total_damage_on_end = shared_data.get("od_damage_on_end", 0)
            total_spherical = shared_data.get("od_spherical_mark", 0)
            others = shared_data.get("od_others", 0)
            
            insert_query = """
            INSERT INTO od_roller_tracking 
            (roller_type, employee_id, report_date, start_time, end_time, 
             total_inspected, total_accepted, total_rejected, 
             total_rust, total_dent, total_damage, 
             total_damage_on_end, total_spherical, others)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            data = (
                roller_type, employee_id, report_date, start_time, end_time,
                total_inspected, total_accepted, total_rejected,
                total_rust, total_dent, total_damage,
                total_damage_on_end, total_spherical, others
            )
            
            cursor.execute(insert_query, data)
            self.connection.commit()
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ Error inserting OD tracking data: {e}")
            traceback.print_exc()
            return False
    
    def save_inspection_session(self, employee_id, start_time, shared_data):
        """
        Save both BF and OD inspection session data.
        
        Args:
            employee_id: Employee ID
            start_time: Start time of inspection
            shared_data: Dictionary containing inspection statistics
        """
        bf_success = self.insert_bf_tracking(employee_id, start_time, shared_data)
        od_success = self.insert_od_tracking(employee_id, start_time, shared_data)
        
        return bf_success and od_success


def save_to_database(employee_id, start_time, shared_data, 
                     host=AppConfig.DB_HOST, user=AppConfig.DB_USER, password=AppConfig.DB_PASSWORD, 
                     database=AppConfig.DB_DATABASE):
    """
    Save inspection data to database.
    
    Args:
        employee_id: Employee ID
        start_time: Start time of inspection
        shared_data: Dictionary containing inspection statistics
        host: MySQL server host
        user: Database username
        password: Database password
        database: Database name
    
    Returns:
        bool: True if successful, False otherwise
    """
    db = RollerDatabase()
    
    if db.connect():
        success = db.save_inspection_session(employee_id, start_time, shared_data)
        db.disconnect()
        return success
    
    return False
