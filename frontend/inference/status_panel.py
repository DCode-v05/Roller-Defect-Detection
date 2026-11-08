"""
Status Panel Component
Displays roller type, date/time, machine mode, disc status, confidence thresholds, and AI models
"""

import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime

from frontend.utils.config import AppConfig
from ..utils.styles import Colors, Fonts
from ..utils.db_error_handler import DatabaseErrorHandler


class StatusPanel:
    """Status information panel at the top of inference tab."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the status panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.status_vars = {}
        
    def create(self):
        """Create the status panel UI."""
        container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        container.pack(anchor=tk.W, padx=5, pady=5)
        
        self._create_roller_type_section(container, 0)
        self._create_datetime_section(container, 1)
        self._create_machine_mode_section(container, 2)
        self._create_disc_status_section(container, 3)
        self._create_confidence_section(container, 4)
        self._create_ai_models_section(container, 5)
        
        for i in range(5):
            container.grid_columnconfigure(i, weight=0, minsize=200)
        container.grid_columnconfigure(5, weight=0, minsize=250)
        
        return container
    
    def _create_section_frame(self, parent, title, column):
        """Create a labeled frame for a status section."""
        frame = tk.LabelFrame(
            parent,
            text=title,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        frame.grid(row=0, column=column, padx=6, pady=2, sticky="nsew")
        return frame
    
    def _create_roller_type_section(self, parent, column):
        """Create roller type section with dropdown."""
        frame = self._create_section_frame(parent, "Roller Type", column)
        
        roller_types = self._get_roller_types()
        
        self.status_vars['roller_type'] = tk.StringVar(value="")
        
        self.roller_dropdown = ttk.Combobox(
            frame,
            textvariable=self.status_vars['roller_type'],
            values=roller_types,
            state="readonly",
            font=Fonts.TEXT,
            width=15
        )
        self.roller_dropdown.pack(padx=8, pady=8, fill=tk.X)
        
        self.roller_dropdown.bind("<<ComboboxSelected>>", self._on_roller_selected)
        
        previously_selected = getattr(self.app, 'selected_roller_type', None)
        
        if previously_selected and previously_selected in roller_types:
            self.roller_dropdown.set(previously_selected)
            self._load_roller_info(previously_selected)
        elif roller_types:
            self.roller_dropdown.set(roller_types[0])
            self._load_roller_info(roller_types[0])
            self.app.selected_roller_type = roller_types[0]
        
        if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
            self.roller_dropdown.config(state="disabled")
    
    def _get_roller_types(self):
        """Get list of roller types from database."""
        def _fetch_rollers():
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT roller_type FROM roller_data ORDER BY roller_type")
            
            roller_types = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            connection.close()
            
            return roller_types if roller_types else ["No Rollers"]
        
        return DatabaseErrorHandler.safe_db_operation(
            _fetch_rollers,
            parent_widget=self.parent,
            context="fetching roller types",
            default_return=["No Rollers"],
            show_error=True
        )
    
    def _on_roller_selected(self, event=None):
        """Handle roller selection from dropdown."""
        selected_roller = self.status_vars['roller_type'].get()
        if selected_roller and selected_roller != "No Rollers":
            self.app.selected_roller_type = selected_roller
            self._load_roller_info(selected_roller)
    
    def _load_roller_info(self, roller_type):
        """Load and display roller information in the roller info panel."""
        try:
            if hasattr(self.app, 'inference_tab') and self.app.inference_tab:
                if hasattr(self.app.inference_tab, 'results_panel') and self.app.inference_tab.results_panel:
                    self.app.inference_tab.results_panel.load_roller_from_db(roller_type)
        
        except Exception as e:
            print(f"❌ Error loading roller info: {e}")
    
    def refresh_roller_list(self):
        """Refresh the roller dropdown list from database and preserve selection."""
        roller_types = self._get_roller_types()
        
        current_selection = self.status_vars['roller_type'].get()
        if not current_selection or current_selection == "No Rollers":
            current_selection = getattr(self.app, 'selected_roller_type', None)
        
        self.roller_dropdown['values'] = roller_types
        
        if current_selection and current_selection in roller_types:
            self.roller_dropdown.set(current_selection)
            self._load_roller_info(current_selection)
            self.app.selected_roller_type = current_selection
        elif roller_types and roller_types[0] != "No Rollers":
            self.roller_dropdown.set(roller_types[0])
            self._load_roller_info(roller_types[0])
            self.app.selected_roller_type = roller_types[0]
        else:
            self.roller_dropdown.set("No Rollers")
    
    def _create_datetime_section(self, parent, column):
        """Create date & time section."""
        frame = self._create_section_frame(parent, "Date & Time", column)
        
        self.status_vars['datetime'] = tk.StringVar(value=datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
        label = tk.Label(
            frame,
            textvariable=self.status_vars['datetime'],
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            height=1
        )
        label.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
        
        self._update_time()
    
    def _update_time(self):
        """Update the time display."""
        self.status_vars['datetime'].set(datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
        self.parent.after(1000, self._update_time)
    
    def _create_machine_mode_section(self, parent, column):
        """Create machine mode section."""
        frame = self._create_section_frame(parent, "Machine Mode", column)
        
        self.status_vars['machine_mode'] = tk.StringVar(value="Not Available")
        self.machine_mode_label = tk.Label(
            frame,
            textvariable=self.status_vars['machine_mode'],
            font=Fonts.TEXT_BOLD,
            fg="#ffff00",
            bg=Colors.PRIMARY_BG,
            height=1
        )
        self.machine_mode_label.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
    
    def _create_disc_status_section(self, parent, column):
        """Create disc status section."""
        frame = self._create_section_frame(parent, "Disc Status", column)
        
        self.status_vars['disc_status'] = tk.StringVar(value="Not Available")
        
        self.disc_label = tk.Label(
            frame,
            textvariable=self.status_vars['disc_status'],
            font=Fonts.TEXT_BOLD,
            fg="#ffff00",
            bg=Colors.PRIMARY_BG,
            height=1
        )
        self.disc_label.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
    
    def _create_confidence_section(self, parent, column):
        """Create confidence thresholds section."""
        frame = self._create_section_frame(parent, "Confidence Thresholds", column)
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=8, pady=5, fill=tk.BOTH, expand=True)
        
        bf_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        bf_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            bf_frame,
            text="BF:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        if self.app.bf_conf_threshold is not None:
            bf_conf_value = f"{int(self.app.bf_conf_threshold * 100)}.0%"
            bf_conf_color = "#00bfff"
        else:
            bf_conf_value = "Not Available"
            bf_conf_color = "#ffff00"
        
        self.status_vars['bf_conf'] = tk.StringVar(value=bf_conf_value)
        self.bf_conf_label = tk.Label(
            bf_frame,
            textvariable=self.status_vars['bf_conf'],
            font=Fonts.TEXT_BOLD,
            fg=bf_conf_color,
            bg=Colors.PRIMARY_BG
        )
        self.bf_conf_label.pack(side=tk.LEFT)
        
        od_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        od_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            od_frame,
            text="OD:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        if self.app.od_conf_threshold is not None:
            od_conf_value = f"{int(self.app.od_conf_threshold * 100)}.0%"
            od_conf_color = "#00bfff"
        else:
            od_conf_value = "Not Available"
            od_conf_color = "#ffff00"
        
        self.status_vars['od_conf'] = tk.StringVar(value=od_conf_value)
        self.od_conf_label = tk.Label(
            od_frame,
            textvariable=self.status_vars['od_conf'],
            font=Fonts.TEXT_BOLD,
            fg=od_conf_color,
            bg=Colors.PRIMARY_BG
        )
        self.od_conf_label.pack(side=tk.LEFT)
    
    def _create_ai_models_section(self, parent, column):
        """Create AI models section."""
        frame = self._create_section_frame(parent, "AI Models", column)
        
        inner_frame = tk.Frame(frame, bg=Colors.PRIMARY_BG)
        inner_frame.pack(padx=8, pady=5, fill=tk.BOTH, expand=True)
        
        bf_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        bf_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            bf_frame,
            text="BF Model:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        bf_model_name = self.app.selected_bf_model_name if self.app.selected_bf_model_name else "No Model Available"
        bf_model_color = "#4CAF50" if self.app.selected_bf_model_path else "#ffff00"
        
        self.status_vars['bf_model'] = tk.StringVar(value=bf_model_name)
        self.bf_model_label = tk.Label(
            bf_frame,
            textvariable=self.status_vars['bf_model'],
            font=Fonts.TEXT_BOLD,
            fg=bf_model_color,
            bg=Colors.PRIMARY_BG
        )
        self.bf_model_label.pack(side=tk.LEFT)
        
        od_frame = tk.Frame(inner_frame, bg=Colors.PRIMARY_BG)
        od_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(
            od_frame,
            text="OD Model:",
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        od_model_name = self.app.selected_od_model_name if self.app.selected_od_model_name else "No Model Available"
        od_model_color = "#4CAF50" if self.app.selected_od_model_path else "#ffff00"
        
        self.status_vars['od_model'] = tk.StringVar(value=od_model_name)
        self.od_model_label = tk.Label(
            od_frame,
            textvariable=self.status_vars['od_model'],
            font=Fonts.TEXT_BOLD,
            fg=od_model_color,
            bg=Colors.PRIMARY_BG
        )
        self.od_model_label.pack(side=tk.LEFT)
    
    def update_disc_status(self, status, color=None):
        """Update disc status display."""
        self.status_vars['disc_status'].set(status)
        if color:
            self.disc_label.config(fg=color)
    
    def update_machine_mode(self, mode, color=None):
        """Update machine mode display."""
        self.status_vars['machine_mode'].set(mode)
        if color:
            self.machine_mode_label.config(fg=color)
    
    def update_confidence_thresholds(self):
        """Update confidence threshold displays."""
        try:
            if self.app.bf_conf_threshold is not None:
                self.status_vars['bf_conf'].set(f"{int(self.app.bf_conf_threshold * 100)}.0%")
                if hasattr(self, 'bf_conf_label') and self.bf_conf_label.winfo_exists():
                    self.bf_conf_label.config(fg="#00bfff")
            else:
                self.status_vars['bf_conf'].set("Not Available")
                if hasattr(self, 'bf_conf_label') and self.bf_conf_label.winfo_exists():
                    self.bf_conf_label.config(fg="#ffff00")
            
            if self.app.od_conf_threshold is not None:
                self.status_vars['od_conf'].set(f"{int(self.app.od_conf_threshold * 100)}.0%")
                if hasattr(self, 'od_conf_label') and self.od_conf_label.winfo_exists():
                    self.od_conf_label.config(fg="#00bfff")
            else:
                self.status_vars['od_conf'].set("Not Available")
                if hasattr(self, 'od_conf_label') and self.od_conf_label.winfo_exists():
                    self.od_conf_label.config(fg="#ffff00")
        except tk.TclError as e:
            print(f"⚠️ Could not update confidence thresholds: Widget no longer exists")
    
    def update_model_names(self):
        """Update AI model names from app."""
        try:
            if hasattr(self.app, 'selected_bf_model_name'):
                bf_model_name = self.app.selected_bf_model_name if self.app.selected_bf_model_name else "No Model Available"
                bf_model_color = "#4CAF50" if self.app.selected_bf_model_path else "#ffff00"
                self.status_vars['bf_model'].set(bf_model_name)
                if hasattr(self, 'bf_model_label') and self.bf_model_label.winfo_exists():
                    self.bf_model_label.config(fg=bf_model_color)
            
            if hasattr(self.app, 'selected_od_model_name'):
                od_model_name = self.app.selected_od_model_name if self.app.selected_od_model_name else "No Model Available"
                od_model_color = "#4CAF50" if self.app.selected_od_model_path else "#ffff00"
                self.status_vars['od_model'].set(od_model_name)
                if hasattr(self, 'od_model_label') and self.od_model_label.winfo_exists():
                    self.od_model_label.config(fg=od_model_color)
        except tk.TclError as e:
            print(f"⚠️ Could not update model names: Widget no longer exists")
    
    def lock_roller_selection(self):
        """Lock the roller type dropdown during inspection."""
        if hasattr(self, 'roller_dropdown') and self.roller_dropdown:
            self.roller_dropdown.config(state="disabled")
    
    def unlock_roller_selection(self):
        """Unlock the roller type dropdown after inspection stops."""
        if hasattr(self, 'roller_dropdown') and self.roller_dropdown:
            self.roller_dropdown.config(state="readonly")
