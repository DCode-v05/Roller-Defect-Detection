"""
Database Error Handler Utility
Centralized error handling for database connection issues
"""

import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from .debug_logger import log_error, log_warning


class DatabaseErrorHandler:
    """Centralized database error handling with user-friendly popups."""
    
    _error_shown_for_page = {}
    _current_page = None
    
    @staticmethod
    def set_current_page(page_name):
        """
        Set the current page/tab name.
        Called when navigating to a new page.
        
        Args:
            page_name: Name of the current page/tab
        """
        DatabaseErrorHandler._current_page = page_name
        if page_name not in DatabaseErrorHandler._error_shown_for_page:
            DatabaseErrorHandler._error_shown_for_page[page_name] = False
    
    @staticmethod
    def reset_error_flag(page_name=None):
        """
        Reset the error shown flag for a page.
        
        Args:
            page_name: Name of the page to reset (defaults to current page)
        """
        if page_name is None:
            page_name = DatabaseErrorHandler._current_page
        
        if page_name:
            DatabaseErrorHandler._error_shown_for_page[page_name] = False
    
    @staticmethod
    def handle_db_error(error, parent_widget=None, context="database operation", show_popup=True):
        """
        Handle database errors with appropriate user feedback.
        
        Args:
            error: The exception/error that occurred
            parent_widget: Parent widget for the message box (optional)
            context: Context description of where the error occurred
            show_popup: Whether to show popup (default True, but controlled by page flag)
        
        Returns:
            bool: False to indicate error occurred
        """
        current_page = DatabaseErrorHandler._current_page
        
        if current_page:
            error_details = {
                "error_type": type(error).__name__,
                "context": context
            }
            
            if isinstance(error, mysql.connector.Error):
                error_details["error_code"] = getattr(error, 'errno', 'Unknown')
                error_details["sql_state"] = getattr(error, 'sqlstate', 'Unknown')
            
            log_error(
                page_name=current_page,
                error_context=f"Database error during {context}",
                exception=error,
                additional_info=error_details
            )
        
        if current_page == "login":
            return False
        
        if current_page and DatabaseErrorHandler._error_shown_for_page.get(current_page, False):
            return False
        
        if show_popup and current_page:
            error_message = str(error)
            
            if isinstance(error, mysql.connector.Error):
                if error.errno == 1045:
                    DatabaseErrorHandler._show_access_denied_error(parent_widget)
                elif error.errno == 2003:
                    DatabaseErrorHandler._show_connection_error(parent_widget)
                elif error.errno == 1049:
                    DatabaseErrorHandler._show_unknown_database_error(parent_widget)
                else:
                    DatabaseErrorHandler._show_generic_db_error(error_message, context, parent_widget)
            else:
                DatabaseErrorHandler._show_generic_db_error(error_message, context, parent_widget)
            
            DatabaseErrorHandler._error_shown_for_page[current_page] = True
        
        return False
    
    @staticmethod
    def _show_access_denied_error(parent_widget=None):
        """Show access denied error popup."""
        messagebox.showerror(
            "Database Connection Error",
            "❌ Access Denied!\n\n"
            "The database username or password is incorrect.\n\n"
            "Please update the database configuration:\n"
            "1. Go to the 'Info' tab\n"
            "2. Scroll to 'MySQL Database Configuration'\n"
            "3. Update your credentials\n"
            "4. Test the connection\n\n"
            "Contact your system administrator if you need help.",
            parent=parent_widget
        )
    
    @staticmethod
    def _show_connection_error(parent_widget=None):
        """Show connection error popup."""
        messagebox.showerror(
            "Database Connection Error",
            "❌ Cannot Connect to MySQL Server!\n\n"
            "Possible reasons:\n"
            "• MySQL service is not running\n"
            "• Incorrect host or port settings\n"
            "• Firewall blocking the connection\n\n"
            "Please check:\n"
            "1. MySQL service is running\n"
            "2. Database configuration in 'Info' tab\n"
            "3. Network and firewall settings\n\n"
            "Contact your system administrator if you need help.",
            parent=parent_widget
        )
    
    @staticmethod
    def _show_unknown_database_error(parent_widget=None):
        """Show unknown database error popup."""
        messagebox.showerror(
            "Database Connection Error",
            "❌ Database Not Found!\n\n"
            "The specified database does not exist on the MySQL server.\n\n"
            "Please:\n"
            "1. Go to the 'Info' tab\n"
            "2. Update the database name in configuration\n"
            "3. Or create the database on your MySQL server\n\n"
            "Contact your system administrator if you need help.",
            parent=parent_widget
        )
    
    @staticmethod
    def _show_generic_db_error(error_message, context, parent_widget=None):
        """Show generic database error popup."""
        messagebox.showerror(
            "Database Error",
            f"❌ Database Error During {context}!\n\n"
            f"Error Details:\n{error_message}\n\n"
            "Please check:\n"
            "1. Database configuration in 'Info' tab\n"
            "2. MySQL service is running\n"
            "3. Your database connection settings\n\n"
            "Contact your system administrator if you need help.",
            parent=parent_widget
        )
    
    @staticmethod
    def test_connection_with_feedback(host, port, user, password, database, parent_widget=None):
        """
        Test database connection and provide user feedback.
        
        Args:
            host: MySQL host
            port: MySQL port
            user: MySQL user
            password: MySQL password
            database: Database name
            parent_widget: Parent widget for message box
        
        Returns:
            tuple: (success: bool, connection or None)
        """
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connection_timeout=5
            )
            
            if connection.is_connected():
                return True, connection
            else:
                return False, None
        
        except mysql.connector.Error as e:
            DatabaseErrorHandler.handle_db_error(e, parent_widget, "connection test")
            return False, None
        except Exception as e:
            DatabaseErrorHandler.handle_db_error(e, parent_widget, "connection test")
            return False, None
    
    @staticmethod
    def safe_db_operation(operation_func, parent_widget=None, context="database operation", 
                         default_return=None, show_error=True):
        """
        Safely execute a database operation with error handling.
        
        Args:
            operation_func: Function to execute (should not take arguments)
            parent_widget: Parent widget for error messages
            context: Context description
            default_return: Value to return on error
            show_error: Whether to show error popup (default True)
        
        Returns:
            Result of operation_func or default_return on error
        """
        try:
            return operation_func()
        except mysql.connector.Error as e:
            print(f"❌ Database error during {context}: {e}")
            if show_error:
                DatabaseErrorHandler.handle_db_error(e, parent_widget, context)
            return default_return
        except Exception as e:
            print(f"❌ Error during {context}: {e}")
            if show_error:
                DatabaseErrorHandler.handle_db_error(e, parent_widget, context)
            return default_return
