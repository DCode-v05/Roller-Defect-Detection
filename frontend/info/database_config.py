"""
MySQL Database Configuration Component
Allows configuration and testing of database connection
"""

import tkinter as tk
from tkinter import messagebox
import mysql.connector
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig


class DatabaseConfig:
    """Component for managing MySQL database configuration."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the database configuration component.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.host_entry = None
        self.port_entry = None
        self.database_entry = None
        self.user_entry = None
        self.password_entry = None
        self.config_text = None
    
    def create(self):
        """Create the database configuration UI."""
        main_frame = tk.LabelFrame(
            self.parent,
            text="🔧 MySQL Database Configuration",
            font=Fonts.HEADER,
            fg="#00FF00",
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.X, padx=10, pady=10)
        
        container = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        container.pack(fill=tk.X, padx=20, pady=15)
        
        section_title = tk.Label(
            container,
            text="🔌 Configure Database Connection",
            font=Fonts.TEXT_BOLD,
            fg="#00FF00",
            bg=Colors.PRIMARY_BG
        )
        section_title.pack(anchor=tk.W, pady=(0, 10))
        
        config_frame = tk.LabelFrame(
            container,
            text="Current Configuration",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=1
        )
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.config_text = tk.Text(
            config_frame,
            font=("Consolas", 9),
            bg="#1E1E1E",
            fg="#00FF00",
            height=4,
            wrap=tk.NONE
        )
        self.config_text.pack(fill=tk.X, padx=10, pady=10)
        self.config_text.config(state=tk.DISABLED)
        
        self._update_config_display()
        
        fields_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        fields_frame.pack(fill=tk.X, pady=10)
        
        self._create_field(fields_frame, "Host:", 0, AppConfig.DB_HOST, "host_entry")
        
        self._create_field(fields_frame, "Port:", 1, str(AppConfig.DB_PORT), "port_entry")
        
        self._create_field(fields_frame, "Database:", 2, AppConfig.DB_DATABASE, "database_entry")
        
        self._create_field(fields_frame, "User:", 3, AppConfig.DB_USER, "user_entry")
        
        self._create_field(fields_frame, "Password:", 4, AppConfig.DB_PASSWORD, "password_entry", show="*")
        
        buttons_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        buttons_frame.pack(pady=15)
        
        tk.Button(
            buttons_frame,
            text="🔍 Test Connection",
            font=Fonts.TEXT_BOLD,
            bg="#17A2B8",
            fg=Colors.WHITE,
            activebackground="#117a8b",
            activeforeground=Colors.WHITE,
            command=self.test_connection,
            width=18,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="💾 Update Configuration",
            font=Fonts.TEXT_BOLD,
            bg="#28A745",
            fg=Colors.WHITE,
            activebackground="#218838",
            activeforeground=Colors.WHITE,
            command=self.update_configuration,
            width=18,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="🔄 Reset to Default",
            font=Fonts.TEXT_BOLD,
            bg="#6C757D",
            fg=Colors.WHITE,
            activebackground="#545b62",
            activeforeground=Colors.WHITE,
            command=self.reset_to_default,
            width=18,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_field(self, parent, label_text, row, default_value, entry_attr, show=None):
        """Create a labeled entry field."""
        field_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        field_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            field_frame,
            text=label_text,
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=12,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5)
        
        entry = tk.Entry(
            field_frame,
            font=Fonts.TEXT,
            bg=Colors.WHITE,
            fg=Colors.PRIMARY_BG,
            width=50,
            show=show
        )
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        entry.insert(0, default_value)
        
        setattr(self, entry_attr, entry)
    
    def _update_config_display(self):
        """Update the current configuration display."""
        config_info = f"""Host: {AppConfig.DB_HOST}
Port: {AppConfig.DB_PORT}
Database: {AppConfig.DB_DATABASE}
User: {AppConfig.DB_USER}"""
        
        self.config_text.config(state=tk.NORMAL)
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, config_info)
        self.config_text.config(state=tk.DISABLED)
    
    def test_connection(self):
        """Test database connection with current values."""
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        database = self.database_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()
        
        if not all([host, port, database, user]):
            messagebox.showerror("Error", "All fields except password are required!")
            return
        
        try:
            port_int = int(port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid number!")
            return
        
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port_int,
                user=user,
                password=password,
                database=database,
                connection_timeout=5
            )
            
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()
                connection.close()
                
                messagebox.showinfo(
                    "Connection Successful",
                    f"✅ Successfully connected to MySQL database!\n\n"
                    f"Host: {host}\n"
                    f"Port: {port_int}\n"
                    f"Database: {database}\n"
                    f"MySQL Version: {version}"
                )
        
        except mysql.connector.Error as e:
            messagebox.showerror(
                "Connection Failed",
                f"❌ Failed to connect to MySQL database!\n\n"
                f"Error: {str(e)}"
            )
        except Exception as e:
            messagebox.showerror(
                "Connection Failed",
                f"❌ An error occurred:\n\n{str(e)}"
            )
    
    def update_configuration(self):
        """Update database configuration in config.py."""
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        database = self.database_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()
        
        if not all([host, port, database, user]):
            messagebox.showerror("Error", "All fields except password are required!")
            return
        
        try:
            port_int = int(port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid number!")
            return
        
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port_int,
                user=user,
                password=password,
                database=database,
                connection_timeout=5
            )
            connection.close()
        except Exception as e:
            response = messagebox.askyesno(
                "Connection Test Failed",
                f"⚠️ Connection test failed:\n{str(e)}\n\n"
                "Do you still want to save these settings?"
            )
            if not response:
                return
        
        AppConfig.DB_HOST = host
        AppConfig.DB_PORT = port_int
        AppConfig.DB_DATABASE = database
        AppConfig.DB_USER = user
        AppConfig.DB_PASSWORD = password
        
        try:
            config_path = r"c:\Welvision Now Working\Welvision\frontend\utils\config.py"
            
            with open(config_path, 'r') as f:
                content = f.read()
            
            import re
            
            content = re.sub(
                r'DB_HOST\s*=\s*"[^"]*"',
                f'DB_HOST = "{host}"',
                content
            )
            content = re.sub(
                r'DB_PORT\s*=\s*\d+',
                f'DB_PORT = {port_int}',
                content
            )
            content = re.sub(
                r'DB_USER\s*=\s*"[^"]*"',
                f'DB_USER = "{user}"',
                content
            )
            content = re.sub(
                r'DB_PASSWORD\s*=\s*"[^"]*"',
                f'DB_PASSWORD = "{password}"',
                content
            )
            content = re.sub(
                r'DB_DATABASE\s*=\s*"[^"]*"',
                f'DB_DATABASE = "{database}"',
                content
            )
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            self._update_config_display()
            
            messagebox.showinfo(
                "Success",
                "✅ Database configuration updated successfully!\n\n"
                "The settings have been saved to config.py"
            )
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to update config.py:\n{str(e)}"
            )
    
    def reset_to_default(self):
        """Reset database configuration to default values."""
        response = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset to default database settings?\n\n"
            "Default settings:\n"
            "Host: localhost\n"
            "Port: 3306\n"
            "User: root\n"
            "Password: root\n"
            "Database: welvision_db"
        )
        
        if response:
            default_host = "localhost"
            default_port = 3306
            default_database = "welvision_db"
            default_user = "root"
            default_password = "root"
            
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, default_host)
            
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, str(default_port))
            
            self.database_entry.delete(0, tk.END)
            self.database_entry.insert(0, default_database)
            
            self.user_entry.delete(0, tk.END)
            self.user_entry.insert(0, default_user)
            
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, default_password)
            
            AppConfig.DB_HOST = default_host
            AppConfig.DB_PORT = default_port
            AppConfig.DB_DATABASE = default_database
            AppConfig.DB_USER = default_user
            AppConfig.DB_PASSWORD = default_password
            
            try:
                config_path = r"c:\Welvision Now Working\Welvision\frontend\utils\config.py"
                
                with open(config_path, 'r') as f:
                    content = f.read()
                
                import re
                
                content = re.sub(
                    r'DB_HOST\s*=\s*"[^"]*"',
                    f'DB_HOST = "{default_host}"',
                    content
                )
                content = re.sub(
                    r'DB_PORT\s*=\s*\d+',
                    f'DB_PORT = {default_port}',
                    content
                )
                content = re.sub(
                    r'DB_USER\s*=\s*"[^"]*"',
                    f'DB_USER = "{default_user}"',
                    content
                )
                content = re.sub(
                    r'DB_PASSWORD\s*=\s*"[^"]*"',
                    f'DB_PASSWORD = "{default_password}"',
                    content
                )
                content = re.sub(
                    r'DB_DATABASE\s*=\s*"[^"]*"',
                    f'DB_DATABASE = "{default_database}"',
                    content
                )
                
                with open(config_path, 'w') as f:
                    f.write(content)
                
                self._update_config_display()
                
                messagebox.showinfo(
                    "Success",
                    "✅ Database configuration reset to default successfully!\n\n"
                    "The default settings have been saved to config.py"
                )
            
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to update config.py:\n{str(e)}"
                )
