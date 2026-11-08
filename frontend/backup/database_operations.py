"""
Database Operations
Core backup and restore functionality using mysqldump and mysql
"""

import os
import subprocess
import shutil
from pathlib import Path
from ..utils.config import AppConfig
from ..utils.debug_logger import log_error, log_warning, log_info


class DatabaseOperations:
    """Static methods for database backup and restore operations."""
    
    @staticmethod
    def _find_mysql_bin_path():
        """
        Find MySQL bin directory containing mysqldump and mysql executables.
        
        Returns:
            str: Path to MySQL bin directory or None if not found
        """
        common_paths = [
            r"C:\Program Files\MySQL\MySQL Server 8.0\bin",
            r"C:\Program Files\MySQL\MySQL Server 8.1\bin",
            r"C:\Program Files\MySQL\MySQL Server 8.2\bin",
            r"C:\Program Files\MySQL\MySQL Server 5.7\bin",
            r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin",
            r"C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin",
            r"C:\xampp\mysql\bin",
            r"C:\wamp64\bin\mysql\mysql8.0.27\bin",
            r"C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin",
        ]
        
        if shutil.which("mysqldump") is not None:
            return ""
        
        for path in common_paths:
            if os.path.exists(path):
                mysqldump_path = os.path.join(path, "mysqldump.exe")
                mysql_path = os.path.join(path, "mysql.exe")
                if os.path.exists(mysqldump_path) and os.path.exists(mysql_path):
                    return path
        
        return None
    
    @staticmethod
    def backup_database(backup_file_path):
        """
        Create a backup of the MySQL database using mysqldump.
        
        Args:
            backup_file_path: Full path where backup file should be saved
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            log_info("backup", f"Starting database backup to: {backup_file_path}")
            
            mysql_bin = DatabaseOperations._find_mysql_bin_path()
            
            if mysql_bin is None:
                error_msg = (
                    "MySQL installation not found. Please ensure MySQL is installed.\n\n"
                    "Common locations checked:\n"
                    "- C:\\Program Files\\MySQL\\\n"
                    "- C:\\xampp\\mysql\\bin\\\n"
                    "- C:\\wamp64\\bin\\mysql\\\n"
                    "- System PATH"
                )
                log_error("backup", "MySQL installation not found", Exception(error_msg))
                return False, error_msg
            
            mysqldump_exe = os.path.join(mysql_bin, "mysqldump.exe") if mysql_bin else "mysqldump"
            
            cmd = [
                mysqldump_exe,
                f"--host={AppConfig.DB_HOST}",
                f"--port={AppConfig.DB_PORT}",
                f"--user={AppConfig.DB_USER}",
                f"--password={AppConfig.DB_PASSWORD}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                "--add-drop-database",
                "--databases",
                AppConfig.DB_DATABASE,
                f"--result-file={backup_file_path}"
            ]
            
            log_info("backup", f"Executing mysqldump command")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error during backup"
                log_error("backup", "mysqldump failed", Exception(error_msg))
                return False, error_msg
            
            if not os.path.exists(backup_file_path):
                error_msg = "Backup file was not created"
                log_error("backup", error_msg, Exception(error_msg))
                return False, error_msg
            
            file_size = os.path.getsize(backup_file_path)
            if file_size < 1024:
                error_msg = f"Backup file is too small ({file_size} bytes). Backup may have failed."
                log_warning("backup", error_msg)
                return False, error_msg
            
            log_info("backup", f"Database backup completed successfully. Size: {file_size} bytes")
            return True, "Backup completed successfully"
        
        except FileNotFoundError as e:
            error_msg = f"mysqldump executable not found: {str(e)}"
            log_error("backup", "mysqldump not found", e)
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error during backup: {str(e)}"
            log_error("backup", "Backup error", e)
            return False, error_msg
    
    @staticmethod
    def restore_database(backup_file_path):
        """
        Restore MySQL database from a backup file.
        
        Args:
            backup_file_path: Full path to the backup SQL file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            log_info("backup", f"Starting database restore from: {backup_file_path}")
            
            if not os.path.exists(backup_file_path):
                error_msg = f"Backup file not found: {backup_file_path}"
                log_error("backup", error_msg, Exception(error_msg))
                return False, error_msg
            
            mysql_bin = DatabaseOperations._find_mysql_bin_path()
            
            if mysql_bin is None:
                error_msg = (
                    "MySQL installation not found. Please ensure MySQL is installed.\n\n"
                    "Common locations checked:\n"
                    "- C:\\Program Files\\MySQL\\\n"
                    "- C:\\xampp\\mysql\\bin\\\n"
                    "- C:\\wamp64\\bin\\mysql\\\n"
                    "- System PATH"
                )
                log_error("backup", "MySQL installation not found", Exception(error_msg))
                return False, error_msg
            
            mysql_exe = os.path.join(mysql_bin, "mysql.exe") if mysql_bin else "mysql"
            
            cmd = [
                mysql_exe,
                f"--host={AppConfig.DB_HOST}",
                f"--port={AppConfig.DB_PORT}",
                f"--user={AppConfig.DB_USER}",
                f"--password={AppConfig.DB_PASSWORD}",
            ]
            
            log_info("backup", f"Executing mysql restore command")
            
            with open(backup_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            result = subprocess.run(
                cmd,
                input=sql_content,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error during restore"
                log_error("backup", "mysql restore failed", Exception(error_msg))
                return False, error_msg
            
            log_info("backup", "Database restore completed successfully")
            return True, "Restore completed successfully"
        
        except FileNotFoundError as e:
            error_msg = f"mysql executable not found: {str(e)}"
            log_error("backup", "mysql not found", e)
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error during restore: {str(e)}"
            log_error("backup", "Restore error", e)
            return False, error_msg
