"""
Results Panel Component
Displays inspection results for Bigface, OD, and Overall
"""

import tkinter as tk

from frontend.utils.config import AppConfig
from ..utils.styles import Colors, Fonts


class ResultsPanel:
    """Results display panel at the bottom of inference tab."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the results panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.result_vars = {}
        
    def create(self):
        """Create the results panel UI."""
        container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        container.pack(anchor=tk.W, padx=5, pady=5)
        
        self._create_bigface_results(container, 0)
        self._create_od_results(container, 1)
        self._create_overall_results(container, 2)
        
        self._create_roller_info(container, 3)
        
        for i in range(4):
            container.grid_columnconfigure(i, weight=0, minsize=310)
        
        return container
    
    def _create_result_section(self, parent, title, column, prefix):
        """Create a result section frame."""
        frame = tk.LabelFrame(
            parent,
            text=title,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        frame.grid(row=0, column=column, padx=8, pady=2, sticky="nsew")
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        self._create_result_row(inner_frame, "Inspected :", f"{prefix}_inspected", 0)
        self._create_result_row(inner_frame, "Ok rollers :", f"{prefix}_ok", 1)
        self._create_result_row(inner_frame, "Not OK rollers:", f"{prefix}_not_ok", 2)
        self._create_result_row(inner_frame, "Percentage:", f"{prefix}_percentage", 3)
        
        return frame
    
    def _create_result_row(self, parent, label_text, var_key, row, defect_type=False):
        """Create a single result row."""
        row_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        row_frame.pack(fill=tk.X, pady=3)
        
        label = tk.Label(
            row_frame,
            text=label_text,
            font=Fonts.TEXT_BOLD if not defect_type else Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="w"
        )
        label.pack(side=tk.LEFT)
        
        self.result_vars[var_key] = tk.StringVar(value="0" if "percentage" not in var_key else "0.0%")
        value_label = tk.Label(
            row_frame,
            textvariable=self.result_vars[var_key],
            font=Fonts.TEXT_BOLD if not defect_type else Fonts.TEXT,
            fg="#00ff00" if "percentage" not in var_key else "#ffff00",
            bg=Colors.PRIMARY_BG,
            anchor="e"
        )
        value_label.pack(side=tk.RIGHT)
    
    def _create_bigface_results(self, parent, column):
        """Create Bigface results section."""
        self._create_result_section(parent, "Bigface Result:", column, "bf")
    
    def _create_od_results(self, parent, column):
        """Create OD results section."""
        self._create_result_section(parent, "OD Result:", column, "od")
    
    def _create_overall_results(self, parent, column):
        """Create Overall results section."""
        self._create_result_section(parent, "Overall Result:", column, "overall")
    
    def _create_roller_info(self, parent, column):
        """Create roller info section with two columns."""
        frame = tk.LabelFrame(
            parent,
            text="Roller Info:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        frame.grid(row=0, column=column, padx=8, pady=2, sticky="nsew")
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        left_col = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self._create_info_row(left_col, "Outer Diameter :", "outer_diameter", "No Data")
        self._create_info_row(left_col, "Dimple Diameter:", "dimple_diameter", "No Data")
        self._create_info_row(left_col, "Small Diameter :", "small_diameter", "No Data")
        
        right_col = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self._create_info_row(right_col, "Roller Length :", "roller_length", "No Data")
        self._create_info_row(right_col, "High Head (pixels):", "high_head", "No Data")
        self._create_info_row(right_col, "Down Head (pixels):", "down_head", "No Data")
        
        self._load_initial_roller_info()
    
    def _create_info_row(self, parent, label_text, var_key, default_value):
        """Create a single roller info row."""
        row_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        row_frame.pack(fill=tk.X, pady=5)
        
        inner_frame = tk.Frame(row_frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(fill=tk.X)
        
        label = tk.Label(
            inner_frame,
            text=label_text,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            anchor="w"
        )
        label.pack(side=tk.LEFT)
        
        self.result_vars[var_key] = tk.StringVar(value=default_value)
        value_label = tk.Label(
            inner_frame,
            textvariable=self.result_vars[var_key],
            font=Fonts.TEXT_BOLD,
            fg="#00bfff",
            bg=Colors.PRIMARY_BG,
            anchor="e"
        )
        value_label.pack(side=tk.RIGHT)
    
    def update_results(self, section, inspected, ok_rollers, not_ok_rollers, percentage):
        """
        Update results for a specific section.
        
        Args:
            section: 'bf', 'od', or 'overall'
            inspected: Number of inspected rollers
            ok_rollers: Number of OK rollers
            not_ok_rollers: Number of not OK rollers
            percentage: Percentage value
        """
        self.result_vars[f"{section}_inspected"].set(str(inspected))
        self.result_vars[f"{section}_ok"].set(str(ok_rollers))
        self.result_vars[f"{section}_not_ok"].set(str(not_ok_rollers))
        self.result_vars[f"{section}_percentage"].set(f"{percentage:.1f}%")
    
    def update_roller_info(self, **kwargs):
        """
        Update roller information.
        
        Args:
            **kwargs: Key-value pairs to update (e.g., outer_diameter="25 mm")
        """
        for key, value in kwargs.items():
            if key in self.result_vars:
                self.result_vars[key].set(value)
    
    def _load_initial_roller_info(self):
        """Load initial roller data from database."""
        try:
            previously_selected = getattr(self.app, 'selected_roller_type', None)
            
            if previously_selected and previously_selected != "No Rollers":
                self.load_roller_from_db(previously_selected)
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
                self.update_roller_info(
                    outer_diameter=f"{result['outer_diameter']} mm",
                    dimple_diameter=f"{result['dimple_diameter']} mm",
                    small_diameter=f"{result['small_diameter']} mm",
                    roller_length=f"{result['length_mm']} mm",
                    high_head=f"{result['high_head_pixels']} pixels",
                    down_head=f"{result['down_head_pixels']} pixels"
                )
                print(f"📋 Loaded first roller from DB: {result['roller_type']}")
        
        except Exception as e:
            print(f"❌ Error loading initial roller info: {e}")
            import traceback
            traceback.print_exc()
    
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
                self.update_roller_info(
                    outer_diameter=f"{result['outer_diameter']} mm",
                    dimple_diameter=f"{result['dimple_diameter']} mm",
                    small_diameter=f"{result['small_diameter']} mm",
                    roller_length=f"{result['length_mm']} mm",
                    high_head=f"{result['high_head_pixels']} pixels",
                    down_head=f"{result['down_head_pixels']} pixels"
                )
            else:
                self.update_roller_info(
                    outer_diameter="No Data",
                    dimple_diameter="No Data",
                    small_diameter="No Data",
                    roller_length="No Data",
                    high_head="No Data",
                    down_head="No Data"
                )
        
        except Exception as e:
            print(f"❌ Error loading roller from database: {e}")
    
    def update_from_shared_data(self, shared_data):
        """
        Update all results from shared_data dictionary.
        
        Args:
            shared_data: Dictionary containing inspection statistics
        """
        bf_inspected = shared_data.get("bf_inspected", 0)
        bf_ok = shared_data.get("bf_ok_rollers", 0)
        bf_not_ok = shared_data.get("bf_not_ok_rollers", 0)
        bf_percentage = (bf_ok / bf_inspected * 100) if bf_inspected > 0 else 0.0
        
        self.result_vars["bf_inspected"].set(str(bf_inspected))
        self.result_vars["bf_ok"].set(str(bf_ok))
        self.result_vars["bf_not_ok"].set(str(bf_not_ok))
        self.result_vars["bf_percentage"].set(f"{bf_percentage:.1f}%")
        
        od_inspected = shared_data.get("od_inspected", 0)
        od_ok = shared_data.get("od_ok_rollers", 0)
        od_not_ok = shared_data.get("od_not_ok_rollers", 0)
        od_percentage = (od_ok / od_inspected * 100) if od_inspected > 0 else 0.0

        self.result_vars["od_inspected"].set(str(od_inspected))
        self.result_vars["od_ok"].set(str(od_ok))
        self.result_vars["od_not_ok"].set(str(od_not_ok))
        self.result_vars["od_percentage"].set(f"{od_percentage:.1f}%")
        
        overall_inspected = bf_inspected
        overall_ok = od_ok
        overall_not_ok = bf_not_ok + od_not_ok
        overall_percentage = (overall_ok / overall_inspected * 100) if overall_inspected > 0 else 0.0
        
        self.result_vars["overall_inspected"].set(str(overall_inspected))
        self.result_vars["overall_ok"].set(str(overall_ok))
        self.result_vars["overall_not_ok"].set(str(overall_not_ok))
        self.result_vars["overall_percentage"].set(f"{overall_percentage:.1f}%")
