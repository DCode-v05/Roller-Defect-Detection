"""
Main Application Class for WelVision System
"""

import tkinter as tk
import numpy as np
import time
from multiprocessing import Process, Array, Queue, Lock, Value, Manager
from ultralytics import YOLO
import snap7
from snap7.util import set_bool
from snap7.type import Areas

from .utils.styles import Colors, Fonts
from .utils.config import AppConfig
from .utils.helpers import center_window, create_header
from .utils.db_error_handler import DatabaseErrorHandler
from .utils.process_manager import ProcessManager, ThreadStopFlag
from .utils.debug_logger import debug_logger, log_error, log_warning, log_info
from .login import LoginPage
from .navbar import NavBarManager
from .inference import InferenceTab
from .info import InfoTab
from .settings import SettingsTab
from .model_management import ModelManagementTab
from .diagnosis import DiagnosisTab
from .system_check import SystemCheckTab
from .data import DataTab
from .user_management import UserManagementTab
from .backup import BackupTab
from backend import (
    plc_communication,
    capture_frames_bigface,
    process_rollers_bigface,
    handle_slot_control_bigface,
    capture_frames_od,
    process_frames_od,
    handle_slot_control_od,
)

import shutil
import gc
import torch
import os

def delete_all_pycache(start_path="."):
    count = 0
    for root, dirs, files in os.walk(start_path):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                full_path = os.path.join(root, dir_name)
                shutil.rmtree(full_path)
                count += 1

def clear_gpu_memory():
    """Clears GPU memory if applicable."""
    try:
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    except ImportError:
        print("⚠️ PyTorch not installed; skipping GPU memory clearance.")

class WelVisionApp(tk.Tk):
    """Main WelVision Application."""
    
    def __init__(self):
        """Initialize the WelVision application."""
        super().__init__()
        
        self.title(AppConfig.WINDOW_TITLE)
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.configure(bg=Colors.PRIMARY_BG)
        self.iconbitmap(default="")
        
        center_window(self, AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)
        
        self.current_user = None
        self.current_role = None
        
        self.od_inspected = 0
        self.od_defective = 0
        self.od_good = 0
        self.bf_inspected = 0
        self.bf_defective = 0
        self.bf_good = 0
        
        self.inspection_running = False
        self.camera_running = False
        self.inspection_has_run = False
        
        self.process_manager = ProcessManager()
        self.camera_stop_flag = ThreadStopFlag()
        
        self.roller_data_updated = False
        
        self.od_defect_thresholds = None
        self.bf_defect_thresholds = None
        
        self.od_conf_threshold = None
        self.bf_conf_threshold = None
        
        self.selected_bf_model_path = None
        self.selected_bf_model_name = None
        self.selected_od_model_path = None
        self.selected_od_model_name = None
        
        self.selected_roller_type = None
        
        self._load_latest_models_from_db()
        
        self.login_page = None
        self.navbar_manager = None
        self.inference_tab = None
        self.info_tab = None
        self.settings_tab = None
        self.model_management_tab = None
        self.diagnosis_tab = None
        self.system_check_tab = None
        self.data_tab = None
        self.user_management_tab = None
        self.backup_tab = None
        
        self.content_frame = None
        self.current_tab_frame = None
        
        self.plc_process = None
        self.processes = []
        self.shared_data = None
        self.manager = None
        
        self.footer_frame = None
        
        self.logout_button = None
        
        self.show_login_page()
    
    def _load_latest_models_from_db(self):
        """Load the latest BF and OD models and their thresholds from database on app startup."""
        try:
            import mysql.connector
            
            connection = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                port=AppConfig.DB_PORT,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_DATABASE
            )
            
            cursor = connection.cursor()
            
            cursor.execute("SELECT model_name, model_path FROM bf_models ORDER BY upload_date DESC LIMIT 1")
            bf_result = cursor.fetchone()
            if bf_result:
                self.selected_bf_model_name = bf_result[0]
                self.selected_bf_model_path = bf_result[1]
                
                cursor.execute("""
                    SELECT model_threshold 
                    FROM bf_threshold_history 
                    WHERE model_name = %s 
                    ORDER BY change_timestamp DESC 
                    LIMIT 1
                """, (self.selected_bf_model_name,))
                bf_threshold_result = cursor.fetchone()
                if bf_threshold_result:
                    self.bf_conf_threshold = float(bf_threshold_result[0])
            else:
                self.selected_bf_model_path = None
                self.selected_bf_model_name = "No Model Available"
            
            cursor.execute("SELECT model_name, model_path FROM od_models ORDER BY upload_date DESC LIMIT 1")
            od_result = cursor.fetchone()
            if od_result:
                self.selected_od_model_name = od_result[0]
                self.selected_od_model_path = od_result[1]
                
                cursor.execute("""
                    SELECT model_threshold 
                    FROM od_threshold_history 
                    WHERE model_name = %s 
                    ORDER BY change_timestamp DESC 
                    LIMIT 1
                """, (self.selected_od_model_name,))
                od_threshold_result = cursor.fetchone()
                if od_threshold_result:
                    self.od_conf_threshold = float(od_threshold_result[0])
            else:
                self.selected_od_model_path = None
                self.selected_od_model_name = "No Model Available"
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            error_msg = f"❌ Error loading latest models from database: {e}"
            print(error_msg)
            log_error("startup", "Failed to load models from database", e, {
                "DB_HOST": AppConfig.DB_HOST,
                "DB_DATABASE": AppConfig.DB_DATABASE
            })
            self.selected_bf_model_path = None
            self.selected_bf_model_name = "No Model Available"
            self.selected_od_model_path = None
            self.selected_od_model_name = "No Model Available"
    
    def reload_models_and_notify_tabs(self):
        """
        Reload models from database and notify Settings and Inference tabs.
        Called when models are uploaded or deleted in Model Management tab.
        """
        
        self._load_latest_models_from_db()
        
        if hasattr(self, 'inference_tab') and self.inference_tab:
            if hasattr(self.inference_tab, 'status_panel') and self.inference_tab.status_panel:
                try:
                    self.inference_tab.status_panel.update_model_names()
                    self.inference_tab.status_panel.update_confidence_thresholds()
                except Exception as e:
                    print(f"⚠️ Could not update Inference status panel: {e}")
        
        if hasattr(self, 'settings_tab') and self.settings_tab:
            current_tab = getattr(self, 'current_tab_id', None)
            if current_tab == 'settings':
                try:
                    was_preview_active = getattr(self.settings_tab, 'preview_active', False)
                    
                    self.settings_tab.parent = self.current_tab_frame
                    self.settings_tab.setup()
                    
                except Exception as e:
                    print(f"⚠️ Could not refresh Settings tab: {e}")
        
                        
    def show_login_page(self):
        """Display the login page."""
        DatabaseErrorHandler.set_current_page("login")
        
        if hasattr(self, 'camera_running') and self.camera_running:
            self.camera_running = False
            self.camera_stop_flag.set()
            time.sleep(0.3)
        
        if hasattr(self, 'inspection_running') and self.inspection_running:
            self.stop_inspection()
        
        self.login_page = LoginPage(self, self.on_login_success)
        self.login_page.show()
        
        self._create_global_footer()
    
    def _create_global_footer(self):
        """Create footer with company name that appears on all pages."""
        if hasattr(self, 'footer_frame') and self.footer_frame:
            self.footer_frame.destroy()
        
        self.footer_frame = tk.Frame(self, bg=Colors.SECONDARY_BG, height=40)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=0)
        self.footer_frame.pack_propagate(False)
        
        company_label = tk.Label(
            self.footer_frame,
            text="Developed and Maintained by © Welvision Pvt Limited",
            font=Fonts.TEXT_BOLD,
            fg="#FFFFFF",
            bg=Colors.SECONDARY_BG
        )
        company_label.pack(expand=True, pady=8)
    
    def on_login_success(self, email, role):
        """
        Handle successful login.
        
        Args:
            email: User email
            role: User role
        """
        self.current_user = email
        self.current_role = role
        self.show_main_interface()
    
    def show_main_interface(self):
        """Display the main application interface."""
        self.initialize_system()
        
        for widget in self.winfo_children():
            widget.destroy()
        
        self._create_global_footer()
        
        main_frame = tk.Frame(self, bg=Colors.PRIMARY_BG)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame, self.logout_button, self.debug_checkbutton = create_header(
            main_frame, 
            AppConfig.WINDOW_TITLE,
            self.current_user, 
            self.current_role, 
            self.show_login_page,
            self
        )
        
        self.navbar_manager = NavBarManager(main_frame, self.on_nav_change, self)
        self.navbar_manager.create()
        
        self.content_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.show_tab("inference")
        
        self.start_camera_feeds()
        
        self.update_statistics()
    
    def initialize_system(self):
        """Initialize the backend inspection system."""
        
        
        self.frame_shape = (
            AppConfig.CAMERA_FRAME_HEIGHT, 
            AppConfig.CAMERA_FRAME_WIDTH, 
            3
        )
        
        self.manager = Manager()
        self.shared_data = self.manager.dict()
        self.shared_data['bigface'] = False
        self.shared_data['od'] = False
        self.shared_data['bigface_presence'] = False
        self.shared_data['od_presence'] = False
        self.shared_data['head_classification'] = False
        self.shared_data['od_conf_threshold'] = self.od_conf_threshold
        self.shared_data['bf_conf_threshold'] = self.bf_conf_threshold
        self.shared_data["bf_ready"] = False
        self.shared_data["od_ready"] = False
        self.shared_data["overall_system_ready"] = False
        self.shared_data["system_mode"] = False 
        self.shared_data["system_ready"] = False 
        self.shared_data["disc_status"] = False 
        self.shared_data["allow_all"] = False
        self.shared_data["debug_enabled"] = False
        
        self.shared_data["bf_inspected"] = 0
        self.shared_data["bf_ok_rollers"] = 0
        self.shared_data["bf_not_ok_rollers"] = 0
        self.shared_data["rust"] = 0
        self.shared_data["dent"] = 0
        self.shared_data["damage"] = 0
        self.shared_data["high_head"] = 0
        self.shared_data["down_head"] = 0
        self.shared_data["others"] = 0
        
        self.shared_data["od_inspected"] = 0
        self.shared_data["od_ok_rollers"] = 0
        self.shared_data["od_not_ok_rollers"] = 0
        self.shared_data["od_rust"] = 0
        self.shared_data["od_dent"] = 0
        self.shared_data["od_damage"] = 0
        self.shared_data["od_damage_on_end"] = 0
        self.shared_data["od_spherical_mark"] = 0
        self.shared_data["od_others"] = 0
        
        self.shared_data["system_check_bf_processed"] = 0
        self.shared_data["system_check_bf_accepted"] = 0
        self.shared_data["system_check_bf_rejected"] = 0
        self.shared_data["system_check_od_processed"] = 0
        self.shared_data["system_check_od_accepted"] = 0
        self.shared_data["system_check_od_rejected"] = 0
        self.shared_data["system_check_total_passed"] = 0
        self.shared_data["system_check_total_accepted"] = 0
        self.shared_data["system_check_total_rejected"] = 0
        
        self.inspection_start_time = None
        
        self.shared_data["system_error"] = False
        
        self.command_queue = Queue()
        
        self.proximity_count_od = Value('i', 0)
        self.proximity_count_bigface = Value('i', 0)
        
        self.roller_data_od = self.manager.dict()
        self.roller_queue_od = Queue()
        self.roller_queue_bigface = Queue()
        self.roller_updation_dict = self.manager.dict()
        
        self.shared_frame_bigface = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        self.shared_frame_od = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        
        self.frame_lock_bigface = Lock()
        self.frame_lock_od = Lock()
        self.queue_lock = Lock()
        
        self.shared_annotated_bigface = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        self.shared_annotated_od = Array('B', np.zeros(self.frame_shape, dtype=np.uint8).flatten())
        
        self.annotated_frame_lock_bigface = Lock()
        self.annotated_frame_lock_od = Lock()
        
        self.PLC_IP = AppConfig.PLC_IP
        self.RACK = AppConfig.PLC_RACK
        self.SLOT = AppConfig.PLC_SLOT
        self.DB_NUMBER = AppConfig.PLC_DB_NUMBER
        
    
    def create_processes(self):
        """Create process instances for backend operations."""
        self.plc_process = Process(
            target=plc_communication,
            args=(self.PLC_IP, self.RACK, self.SLOT, self.DB_NUMBER, self.shared_data, self.command_queue),
            daemon=True
        )
        self.process_manager.register_plc_process(self.plc_process)
        
        self.processes = [
            Process(
                target=capture_frames_bigface, 
                args=(self.shared_frame_bigface, self.frame_lock_bigface, self.frame_shape, self.shared_data), 
                daemon=True
            ),
            Process(
                target=handle_slot_control_bigface, 
                args=(self.roller_queue_bigface, self.shared_data, self.command_queue), 
                daemon=True
            ),
            Process(
                target=process_rollers_bigface, 
                args=(
                    self.shared_frame_bigface, 
                    self.frame_lock_bigface, 
                    self.roller_queue_bigface, 
                    self.selected_bf_model_path, 
                    self.proximity_count_bigface, 
                    self.roller_updation_dict, 
                    self.queue_lock, 
                    self.shared_data, 
                    self.frame_shape, 
                    self.shared_annotated_bigface, 
                    self.annotated_frame_lock_bigface
                ), 
                daemon=True
            ),
            Process(
                target=process_frames_od, 
                args=(
                    self.shared_frame_od, 
                    self.frame_lock_od, 
                    self.roller_queue_od,
                    self.selected_od_model_path, 
                    self.queue_lock, 
                    self.shared_data, 
                    self.frame_shape, 
                    self.roller_updation_dict, 
                    self.shared_annotated_od, 
                    self.annotated_frame_lock_od
                ), 
                daemon=True
            ),
            Process(
                target=capture_frames_od, 
                args=(self.shared_frame_od, self.frame_lock_od, self.frame_shape, self.shared_data), 
                daemon=True
            ),
            Process(
                target=handle_slot_control_od, 
                args=(self.roller_queue_od, self.shared_data, self.command_queue), 
                daemon=True
            )
        ]
        
        for process in self.processes:
            self.process_manager.register_inference_process(process)
    
    def start_inspection(self):
        """Start the inspection process."""
        page_name = getattr(self, 'current_tab_id', 'inference')
        
        try:
            if self.inspection_running:
                log_warning(page_name, "Attempted to start inspection while already running")
                print("Inspection is already running!")
                return
            
            log_info(page_name, "Starting inspection process")
            
            if hasattr(self, 'shared_data'):
                self.shared_data['system_error'] = False
            
            self.inspection_running = True
            if self.inference_tab and self.inference_tab.control_panel:
                self.inference_tab.control_panel.enable_stop()
            
            from datetime import datetime
            self.inspection_start_time = datetime.now().time()
            log_info(page_name, f"Inspection start time: {self.inspection_start_time}")
            
            self.create_processes()
            
            if self.plc_process is not None:
                self.plc_process.start()
                log_info(page_name, "PLC process started")
            
            for idx, process in enumerate(self.processes):
                process.start()
                log_info(page_name, f"Subprocess {idx+1}/{len(self.processes)} started")
            
            log_info(page_name, "✅ Inspection started successfully")
            
            self._monitor_system_error()
            
        except Exception as e:
            log_error(page_name, "Failed to start inspection", e, {
                "inspection_running": self.inspection_running,
                "selected_bf_model": getattr(self, 'selected_bf_model_name', 'Unknown'),
                "selected_od_model": getattr(self, 'selected_od_model_name', 'Unknown')
            })
            self.inspection_running = False
            if self.inference_tab and self.inference_tab.control_panel:
                self.inference_tab.control_panel.enable_start()
            raise
        
    
    def stop_inspection(self):
        """Stop the inspection process with proper cleanup."""
        page_name = getattr(self, 'current_tab_id', 'inference')
        
        try:
            if not self.inspection_running:
                log_warning(page_name, "Attempted to stop inspection when not running")
                print("Inspection is not running.")
                return
            
            log_info(page_name, "Stopping inspection process")
            
            plc_client = snap7.client.Client() 
            try:
                plc_client.connect(self.PLC_IP, self.RACK, self.SLOT)
                
                data = plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
                set_bool(data, byte_index=1, bool_index=6, value=False)
                set_bool(data, byte_index=1, bool_index=7, value=False)
                plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                
                plc_client.disconnect()
                log_info(page_name, "PLC lights turned off")
            except Exception as e:
                log_error(page_name, "Failed to turn off PLC lights", e, {
                    "PLC_IP": self.PLC_IP,
                    "RACK": self.RACK,
                    "SLOT": self.SLOT
                })
            
            self.inspection_running = False
            if self.inference_tab and self.inference_tab.control_panel:
                self.inference_tab.control_panel.enable_start()
            
            self.process_manager.stop_all_inference()
            log_info(page_name, "All inference processes stopped")
            
            self.process_manager.cleanup_gpu_memory()
            log_info(page_name, "GPU memory cleaned up")
            
            self.plc_process = None
            self.processes = []
            
            if hasattr(self, 'inference_tab') and self.inference_tab:
                if hasattr(self.inference_tab, 'camera_manager') and self.inference_tab.camera_manager:
                    for feed_id in ['bf', 'od']:
                        feed = self.inference_tab.camera_manager.get_feed(feed_id)
                        if feed and hasattr(feed, 'cleanup'):
                            feed.cleanup()
            
            import gc
            gc.collect()
            
            time.sleep(0.3)
            
            log_info(page_name, "✅ Inspection stopped successfully")
            
        except Exception as e:
            log_error(page_name, "Error during inspection stop", e)
            
    def on_nav_change(self, button_id):
        """
        Handle navigation button click.
        
        Args:
            button_id: ID of the clicked navigation button
        """
        self.show_tab(button_id)
    
    def show_tab(self, tab_id):
        """
        Show the specified tab with optimized switching.
        
        Args:
            tab_id: ID of the tab to show
        """
        self.current_tab_id = tab_id
        
        if hasattr(self, 'debug_var') and hasattr(self, 'debug_checkbutton'):
            is_enabled = debug_logger.is_enabled(tab_id)
            self.debug_var.set(is_enabled)
            if is_enabled:
                self.debug_checkbutton.config(fg="#00ff00")
            else:
                self.debug_checkbutton.config(fg=Colors.WHITE)
        
        DatabaseErrorHandler.set_current_page(tab_id)
        
        log_info(tab_id, f"Navigated to {tab_id} page")
        
        try:
            previous_settings_tab = None
            if hasattr(self, 'settings_tab') and self.settings_tab is not None:
                if hasattr(self.settings_tab, 'preview_active') and self.settings_tab.preview_active:
                    previous_settings_tab = self.settings_tab
                elif tab_id != "settings":
                    try:
                        if hasattr(self.settings_tab, 'cleanup'):
                            self.settings_tab.cleanup()
                    except Exception as e:
                        log_error(tab_id, "Failed to cleanup settings tab", e)
            
            if hasattr(self, 'info_tab') and self.info_tab is not None and tab_id != "info":
                try:
                    if hasattr(self.info_tab, 'cleanup'):
                        self.info_tab.cleanup()
                except Exception as e:
                    log_error(tab_id, "Failed to cleanup info tab", e)
            
            if self.current_tab_frame:
                old_frame = self.current_tab_frame
                self.after(10, lambda: old_frame.destroy() if old_frame.winfo_exists() else None)
            
            self.current_tab_frame = tk.Frame(self.content_frame, bg=Colors.PRIMARY_BG)
            self.current_tab_frame.pack(fill=tk.BOTH, expand=True)
            
            self._setup_tab_content(tab_id, previous_settings_tab)
            
            if self.navbar_manager:
                self.navbar_manager.set_active_button(tab_id)
                
        except Exception as e:
            log_error(tab_id, f"Failed to show {tab_id} tab", e, {
                "current_user": self.current_user,
                "current_role": self.current_role
            })
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Tab Load Error",
                f"Failed to load {tab_id} tab.\n\nError: {str(e)}\n\n"
                f"Check debug logs for details."
            )
    
    def _setup_tab_content(self, tab_id, previous_settings_tab=None):
        """
        Setup tab content with error handling for each tab.
        
        Args:
            tab_id: ID of the tab to setup
            previous_settings_tab: Previous settings tab instance (if restoring)
        """
        try:
            if tab_id == "inference":
                log_info(tab_id, "Setting up Inference tab")
                self.inference_tab = InferenceTab(self.current_tab_frame, self)
                self.inference_tab.setup()
                if self.camera_running:
                    self.start_camera_feeds()
            
            elif tab_id == "data":
                log_info(tab_id, "Setting up Data tab")
                self.data_tab = DataTab(self.current_tab_frame, self)
                self.data_tab.setup()
            
            elif tab_id == "diagnosis":
                log_info(tab_id, "Setting up Diagnosis tab")
                self.diagnosis_tab = DiagnosisTab(self.current_tab_frame, self)
                self.diagnosis_tab.setup()
            
            elif tab_id == "settings":
                log_info(tab_id, "Setting up Settings tab")
                if previous_settings_tab is not None:
                    self.settings_tab = previous_settings_tab
                    self.settings_tab.parent = self.current_tab_frame
                    self.settings_tab.setup()
                else:
                    self.settings_tab = SettingsTab(self.current_tab_frame, self)
                    self.settings_tab.setup()
            
            elif tab_id == "model_management":
                log_info(tab_id, "Setting up Model Management tab")
                self.model_management_tab = ModelManagementTab(self.current_tab_frame, self)
                self.model_management_tab.setup()
            
            elif tab_id == "user_management":
                log_info(tab_id, "Setting up User Management tab")
                self.user_management_tab = UserManagementTab(self.current_tab_frame, self)
                self.user_management_tab.setup()
            
            elif tab_id == "system_check":
                log_info(tab_id, "Setting up System Check tab")
                self.system_check_tab = SystemCheckTab(self.current_tab_frame, self)
                self.system_check_tab.setup()
            
            elif tab_id == "backup":
                log_info(tab_id, "Setting up Backup tab")
                self.backup_tab = BackupTab(self.current_tab_frame, self)
                self.backup_tab.setup()
            
            elif tab_id == "info":
                log_info(tab_id, "Setting up Info tab")
                self.info_tab = InfoTab(self.current_tab_frame, self)
                self.info_tab.setup()
            
            log_info(tab_id, f"{tab_id} tab setup completed successfully")
            
        except Exception as e:
            log_error(tab_id, f"Error during {tab_id} tab setup", e)
            raise
    
    def _show_placeholder_tab(self, title, description):
        """
        Show a placeholder tab for unimplemented features.
        
        Args:
            title: Tab title
            description: Tab description
        """
        container = tk.Frame(self.current_tab_frame, bg=Colors.PRIMARY_BG)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            container,
            text=title,
            font=Fonts.LARGE,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(50, 20))
        
        desc_label = tk.Label(
            container,
            text=description,
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        desc_label.pack(pady=10)
        
        info_label = tk.Label(
            container,
            text="This feature is under development",
            font=Fonts.SMALL,
            fg="#888888",
            bg=Colors.PRIMARY_BG
        )
        info_label.pack(pady=10)
    
    def start_camera_feeds(self):
        """Start camera feed update threads."""
        self.camera_running = True
        if self.inference_tab:
            self.inference_tab.start_camera_threads()
    
    def update_statistics(self):
        """Update statistics display (mock data for now)."""
        if hasattr(self, 'od_inspected_var') and self.inspection_running:
            if np.random.random() < 0.2:
                self.od_inspected += 1
                defect = np.random.random() < 0.3
                if defect:
                    self.od_defective += 1
                else:
                    self.od_good += 1
                
                self.od_inspected_var.set(str(self.od_inspected))
                self.od_defective_var.set(str(self.od_defective))
                self.od_good_var.set(str(self.od_good))
                
                if self.od_inspected > 0:
                    proportion = (self.od_defective / self.od_inspected) * 100
                    self.od_proportion_var.set(f"{proportion:.1f}%")
            
            if np.random.random() < 0.2:
                self.bf_inspected += 1
                defect = np.random.random() < 0.2
                if defect:
                    self.bf_defective += 1
                else:
                    self.bf_good += 1
                
                self.bf_inspected_var.set(str(self.bf_inspected))
                self.bf_defective_var.set(str(self.bf_defective))
                self.bf_good_var.set(str(self.bf_good))
                
                if self.bf_inspected > 0:
                    proportion = (self.bf_defective / self.bf_inspected) * 100
                    self.bf_proportion_var.set(f"{proportion:.1f}%")
            
            total_inspected = self.od_inspected + self.bf_inspected
            total_defective = self.od_defective + self.bf_defective
            total_good = self.od_good + self.bf_good
            
            self.total_inspected_var.set(str(total_inspected))
            self.total_defective_var.set(str(total_defective))
            self.total_good_var.set(str(total_good))
            
            if total_inspected > 0:
                total_proportion = (total_defective / total_inspected) * 100
                self.total_proportion_var.set(f"{total_proportion:.1f}%")
        
        self.after(100, self.update_statistics)
    
    def update_threshold(self, val, label, defect, is_od):
        """
        Update threshold value label.
        
        Args:
            val: New threshold value
            label: Label widget to update
            defect: Defect type name
            is_od: Whether this is an OD threshold
        """
        label.config(text=f"{int(float(val))}%")
        
        if is_od:
            self.od_defect_thresholds[defect] = int(float(val))
        else:
            self.bf_defect_thresholds[defect] = int(float(val))
    
    def update_model_confidence(self):
        """Update model confidence thresholds in real-time."""
        if not hasattr(self, 'inspection_running') or not self.inspection_running:
            return
        
        od_conf = self.od_conf_threshold
        bf_conf = self.bf_conf_threshold
                
        if hasattr(self, 'shared_data'):
            self.shared_data['od_conf_threshold'] = od_conf
            self.shared_data['bf_conf_threshold'] = bf_conf
    
    def _monitor_system_error(self):
        """Monitor for system errors and handle them."""
        if hasattr(self, 'shared_data') and self.shared_data:
            if self.shared_data.get('system_error', False):
                self.shared_data['system_error'] = False
                
                self._show_system_error_popup()
        
        is_any_system_running = (
            (hasattr(self, 'inspection_running') and self.inspection_running) or
            (hasattr(self, 'system_check_running') and self.system_check_running)
        )
        
        if is_any_system_running:
            self.after(500, self._monitor_system_error)
    
    def _show_system_error_popup(self):
        """Show error popup and stop all processes."""
        from tkinter import messagebox
        
        error_in_inference = hasattr(self, 'inspection_running') and self.inspection_running
        error_in_settings = hasattr(self, 'settings_tab') and self.settings_tab and hasattr(self.settings_tab, 'preview_active') and self.settings_tab.preview_active
        error_in_system_check = hasattr(self, 'system_check_tab') and self.system_check_tab and hasattr(self.system_check_tab, 'system_running') and self.system_check_tab.system_running
        
        if error_in_inference:
            try:
                plc_client = snap7.client.Client() 
                try:
                    plc_client.connect(self.PLC_IP, self.RACK, self.SLOT)
                    
                    data = plc_client.read_area(Areas.DB, self.DB_NUMBER, 0, 2)
                    set_bool(data, byte_index=1, bool_index=6, value=False)
                    set_bool(data, byte_index=1, bool_index=7, value=False)
                    plc_client.write_area(Areas.DB, self.DB_NUMBER, 0, data)
                    
                    plc_client.disconnect()
                except:
                    pass
                
                self.inspection_running = False
                if self.inference_tab and self.inference_tab.control_panel:
                    self.inference_tab.control_panel.enable_start()
                
                self.process_manager.stop_all_inference()
                
                self.process_manager.cleanup_gpu_memory()
                
                self.plc_process = None
                self.processes = []
                
            except Exception as e:
                print(f"❌ Error during emergency shutdown: {e}")
        
        if error_in_settings:
            try:
                self.settings_tab.preview_active = False
                if self.settings_tab.preview_stop_flag:
                    self.settings_tab.preview_stop_flag.set()
                
                try:
                    plc_client = snap7.client.Client()
                    plc_client.connect("172.17.8.17", 0, 1)
                    data = plc_client.read_area(Areas.DB, 86, 0, 2)
                    set_bool(data, byte_index=1, bool_index=6, value=False)
                    set_bool(data, byte_index=1, bool_index=7, value=False)
                    plc_client.write_area(Areas.DB, 86, 0, data)
                    plc_client.disconnect()
                except:
                    pass
                
                if self.settings_tab.preview_bf_model is not None:
                    del self.settings_tab.preview_bf_model
                    self.settings_tab.preview_bf_model = None
                
                if self.settings_tab.preview_od_model is not None:
                    del self.settings_tab.preview_od_model
                    self.settings_tab.preview_od_model = None
                
                if self.settings_tab.preview_bf_camera_process is not None:
                    self.process_manager.register_preview_process(self.settings_tab.preview_bf_camera_process)
                
                if self.settings_tab.preview_od_camera_process is not None:
                    self.process_manager.register_preview_process(self.settings_tab.preview_od_camera_process)
                
                self.process_manager.stop_all_preview()
                
                self.settings_tab.preview_bf_camera_process = None
                self.settings_tab.preview_od_camera_process = None
                
                self.settings_tab._unblock_navigation_buttons()
                self.settings_tab._unblock_logout_button()
                self.settings_tab._unblock_model_dropdowns()
                self.settings_tab._unblock_save_button()
                
                if self.settings_tab.preview_control_panel:
                    self.settings_tab.preview_control_panel.enable_start()
                
            except Exception as e:
                print(f"❌ Error stopping settings preview: {e}")
        
        if error_in_system_check:
            try:
                if self.system_check_tab.plc_controller:
                    self.system_check_tab.plc_controller.stop_monitoring()
                
                self.system_check_tab.system_running = False
                self.system_check_tab.app.system_check_running = False
                
                self.system_check_tab._unblock_navigation_buttons()
                self.system_check_tab._unblock_logout_button()
                
                if self.system_check_tab.control_settings:
                    self.system_check_tab.control_settings.enable_controls()
                    self.system_check_tab.controls_are_disabled = False
                    self.system_check_tab.app.system_check_controls_disabled = False
                
                if self.system_check_tab.system_control:
                    self.system_check_tab.system_control.enable_start()
                
            except Exception as e:
                print(f"❌ Error stopping system check: {e}")
        
        if hasattr(self, 'on_closing'):
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.process_manager.cleanup_gpu_memory()
        
        messagebox.showerror(
            "System Error Detected",
            "⚠️ A critical system error has occurred!\n\n"
            "The inspection process has been stopped automatically.\n\n"
            "Possible causes:\n"
            "• GPU memory overflow\n"
            "• Model inference failure\n"
            "• Camera disconnection\n"
            "• PLC communication error\n\n"
            "Recommended action:\n"
            "Please restart the application to clear the error state.\n\n"
            "Click OK to continue using other features."
        )
    
    def on_closing(self):
        """Handle application closing."""
        from tkinter import messagebox
        
        if hasattr(self, 'settings_tab') and self.settings_tab:
            if hasattr(self.settings_tab, 'preview_active') and self.settings_tab.preview_active:
                response = messagebox.askyesno(
                    "Preview Active",
                    "Settings preview is currently running.\n\n"
                    "Closing the application will stop the preview.\n\n"
                    "Do you want to close anyway?"
                )
                if not response:
                    return  
        
        response = messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to close the application?"
        )
        
        if not response:
            return
        
        print("Closing application...")
        self.camera_running = False
        self.camera_stop_flag.set()
        
        if self.inspection_running:
            self.stop_inspection()
        
        self.process_manager.stop_everything()
        
        delete_all_pycache(".")
        self.process_manager.cleanup_gpu_memory()

        time.sleep(0.5)
        self.destroy()