"""
Debug Logger Module
Captures and logs errors in user-understandable format for each page
"""

import os
import traceback
from datetime import datetime
from pathlib import Path


class DebugLogger:
    """Singleton class to manage debug logging across all pages."""
    
    _instance = None
    _enabled_pages = set()
    _log_dir = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugLogger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the debug logger."""
        username = os.getlogin()
        self._log_dir = Path(f"C:\\Users\\{username}\\Desktop\\Debug Logs")
        self._log_dir.mkdir(parents=True, exist_ok=True)
    
    def enable_page(self, page_name):
        """Enable debug logging for a specific page."""
        if page_name not in self._enabled_pages:
            self._enabled_pages.add(page_name)
            self._log_message(page_name, "INFO", f"Debug mode ENABLED for {page_name} page")
            print(f"📝 Debug logging ENABLED for: {page_name}")
    
    def disable_page(self, page_name):
        """Disable debug logging for a specific page."""
        if page_name in self._enabled_pages:
            self._log_message(page_name, "INFO", f"Debug mode DISABLED for {page_name} page")
            self._enabled_pages.discard(page_name)
            print(f"📝 Debug logging DISABLED for: {page_name}")
    
    def is_enabled(self, page_name):
        """Check if debug logging is enabled for a page."""
        return page_name in self._enabled_pages
    
    def toggle_page(self, page_name):
        """Toggle debug logging for a specific page."""
        if self.is_enabled(page_name):
            self.disable_page(page_name)
            return False
        else:
            self.enable_page(page_name)
            return True
    
    def log_error(self, page_name, error_context, exception=None, additional_info=None):
        """
        Log an error with user-understandable description.
        
        Args:
            page_name: Name of the page where error occurred
            error_context: Brief description of what was being done
            exception: Exception object (if available)
            additional_info: Dictionary with additional context
        """
        if not self.is_enabled(page_name):
            return
        
        error_type = type(exception).__name__ if exception else "Error"
        error_msg = str(exception) if exception else "Unknown error"
        
        user_message = f"""
╔══════════════════════════════════════════════════════════════════╗
║ ERROR DETECTED                                                   ║
╚══════════════════════════════════════════════════════════════════╝

Page: {page_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

WHAT HAPPENED:
{error_context}

ERROR TYPE:
{error_type}

ERROR MESSAGE:
{error_msg}
"""
        
        if additional_info:
            user_message += "\nADDITIONAL INFORMATION:\n"
            for key, value in additional_info.items():
                user_message += f"  • {key}: {value}\n"
        
        if exception:
            user_message += "\n" + "─" * 70 + "\n"
            user_message += "TECHNICAL DETAILS (for developers):\n"
            user_message += "─" * 70 + "\n"
            user_message += traceback.format_exc()
        
        user_message += "\n" + "═" * 70 + "\n\n"
        
        self._write_to_file(page_name, user_message)
        
        print(f"❌ ERROR logged in {page_name}: {error_context}")
    
    def log_warning(self, page_name, warning_context, details=None):
        """
        Log a warning message.
        
        Args:
            page_name: Name of the page
            warning_context: Description of the warning
            details: Additional details
        """
        if not self.is_enabled(page_name):
            return
        
        user_message = f"""
╔══════════════════════════════════════════════════════════════════╗
║ WARNING                                                          ║
╚══════════════════════════════════════════════════════════════════╝

Page: {page_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

WARNING:
{warning_context}
"""
        
        if details:
            user_message += f"\nDETAILS:\n{details}\n"
        
        user_message += "\n" + "═" * 70 + "\n\n"
        
        self._write_to_file(page_name, user_message)
        print(f"⚠️ WARNING logged in {page_name}: {warning_context}")
    
    def log_info(self, page_name, info_message):
        """
        Log an informational message.
        
        Args:
            page_name: Name of the page
            info_message: Information to log
        """
        if not self.is_enabled(page_name):
            return
        
        user_message = f"""
[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {page_name}
{info_message}

"""
        
        self._write_to_file(page_name, user_message)
    
    def _log_message(self, page_name, level, message):
        """Internal method to log a message."""
        user_message = f"""
[{level}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {page_name}
{message}

"""
        self._write_to_file(page_name, user_message)
    
    def _write_to_file(self, page_name, message):
        """Write message to the appropriate log file."""
        now = datetime.now()
        month_name = now.strftime('%B')
        date = now.strftime('%d')
        hour = now.strftime('%H')
        minute = now.strftime('%M')
        
        log_file = self._log_dir / f"{page_name}_{month_name}_{date}_{hour}_{minute}.log"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(message)
        except Exception as e:
            print(f"❌ Failed to write to debug log: {e}")
    
    def get_log_file_path(self, page_name):
        """Get the current log file path for a page."""
        now = datetime.now()
        month_name = now.strftime('%B')
        date = now.strftime('%d')
        hour = now.strftime('%H')
        minute = now.strftime('%M')
        return self._log_dir / f"{page_name}_{month_name}_{date}_{hour}_{minute}.log"


debug_logger = DebugLogger()


def enable_debug(page_name):
    """Enable debug logging for a page."""
    debug_logger.enable_page(page_name)


def disable_debug(page_name):
    """Disable debug logging for a page."""
    debug_logger.disable_page(page_name)


def toggle_debug(page_name):
    """Toggle debug logging for a page."""
    return debug_logger.toggle_page(page_name)


def is_debug_enabled(page_name):
    """Check if debug is enabled for a page."""
    return debug_logger.is_enabled(page_name)


def log_error(page_name, error_context, exception=None, additional_info=None):
    """Log an error."""
    debug_logger.log_error(page_name, error_context, exception, additional_info)


def log_warning(page_name, warning_context, details=None):
    """Log a warning."""
    debug_logger.log_warning(page_name, warning_context, details)


def log_info(page_name, info_message):
    """Log info."""
    debug_logger.log_info(page_name, info_message)
