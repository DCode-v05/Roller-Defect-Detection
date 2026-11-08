"""
Roller Info Panel Component
Displays detailed roller information on the right side
"""

import tkinter as tk

from frontend.utils.config import AppConfig
from ..utils.styles import Colors, Fonts


class RollerInfoPanel:
    """Roller information display panel."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the roller info panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.info_vars = {}
        
    def create(self):
        """Create the roller info panel UI."""
        frame = tk.LabelFrame(
            self.parent,
            text="Roller Info:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self._create_info_row(inner_frame, "Outer Diameter :", "outer_diameter", "No Data", 0)
        self._create_info_row(inner_frame, "Dimple Diameter:", "dimple_diameter", "No Data", 1)
        self._create_info_row(inner_frame, "Small Diameter :", "small_diameter", "No Data", 2)
        self._create_info_row(inner_frame, "Roller Length :", "roller_length", "No Data", 3)
        self._create_info_row(inner_frame, "High Head (pixels):", "high_head", "No Data", 4)
        self._create_info_row(inner_frame, "Down Head (pixels):", "down_head", "No Data", 5)
        
        self._load_initial_data()
        
        return frame
    
    def _load_initial_data(self):
        """Load initial roller data from database."""
        try:
            if hasattr(self.app, 'inference_tab') and self.app.inference_tab:
                if hasattr(self.app.inference_tab, 'status_panel') and self.app.inference_tab.status_panel:
                    status_panel = self.app.inference_tab.status_panel
                    if hasattr(status_panel, 'status_vars') and 'roller_type' in status_panel.status_vars:
                        selected_roller = status_panel.status_vars['roller_type'].get()
                        if selected_roller and selected_roller != "No Rollers":
                            self.load_roller_from_db(selected_roller)
                            return
            
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT roller_type, outer_diameter, dimple_diameter, small_diameter, 
                       length_mm, high_head_pixels, down_head_pixels
                FROM roller_data
                ORDER BY roller_type
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                self.update_info(
                    outer_diameter=f"{result['outer_diameter']} mm",
                    dimple_diameter=f"{result['dimple_diameter']} mm",
                    small_diameter=f"{result['small_diameter']} mm",
                    roller_length=f"{result['length_mm']} mm",
                    high_head=f"{result['high_head_pixels']} pixels",
                    down_head=f"{result['down_head_pixels']} pixels"
                )
        
        except Exception as e:
            print(f"❌ Error loading initial roller data: {e}")
    
    def load_roller_from_db(self, roller_type):
        """
        Load roller information from database by roller type.
        
        Args:
            roller_type: Name of the roller type to load
        """
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT outer_diameter, dimple_diameter, small_diameter, 
                       length_mm, high_head_pixels, down_head_pixels
                FROM roller_data
                WHERE roller_type = %s
            """
            cursor.execute(query, (roller_type,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                self.update_info(
                    outer_diameter=f"{result['outer_diameter']} mm",
                    dimple_diameter=f"{result['dimple_diameter']} mm",
                    small_diameter=f"{result['small_diameter']} mm",
                    roller_length=f"{result['length_mm']} mm",
                    high_head=f"{result['high_head_pixels']} pixels",
                    down_head=f"{result['down_head_pixels']} pixels"
                )
            else:
                self.update_info(
                    outer_diameter="No Data",
                    dimple_diameter="No Data",
                    small_diameter="No Data",
                    roller_length="No Data",
                    high_head="No Data",
                    down_head="No Data"
                )
        
        except Exception as e:
            print(f"❌ Error loading roller from database: {e}")
    
    def _create_info_row(self, parent, label_text, var_key, default_value, row):
        """Create a single info row."""
        row_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        row_frame.pack(fill=tk.X, pady=3)
        
        label = tk.Label(
            row_frame,
            text=label_text,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.info_vars[var_key] = tk.StringVar(value=default_value)
        value_label = tk.Label(
            row_frame,
            textvariable=self.info_vars[var_key],
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="e"
        )
        value_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def update_info(self, **kwargs):
        """
        Update roller information.
        
        Args:
            **kwargs: Key-value pairs to update (e.g., outer_diameter="25 mm")
        """
        for key, value in kwargs.items():
            if key in self.info_vars:
                self.info_vars[key].set(value)
