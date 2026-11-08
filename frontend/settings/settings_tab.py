"""
Settings Tab UI Component
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import snap7
from snap7.type import Areas
from snap7.util import set_bool
import threading
import numpy as np
import time
import torch
import cv2
from ultralytics import YOLO
from multiprocessing import Process
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig
from ..utils.process_manager import ThreadStopFlag
from ..utils.debug_logger import log_error, log_warning, log_info
from .preview_camera_feed import PreviewCameraManager
from .preview_control_panel import PreviewControlPanel
from .model_selector import ModelSelector
from .threshold_manager import ThresholdManager
from .threshold_database import ThresholdDatabase

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend import capture_frames_bigface, capture_frames_od


class SettingsTab:
    """Settings tab for model configuration."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the settings tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.preview_camera_manager = None
        self.preview_control_panel = None
        self.model_selector = None
        self.threshold_manager = None
        self.preview_active = False
        self.preview_od_thread = None
        self.preview_bf_thread = None
        self.preview_stop_flag = None
        
        self.preview_bf_model = None
        self.preview_od_model = None
        
        self.preview_bf_camera_process = None
        self.preview_od_camera_process = None
        
        self.threshold_snapshot = None
        
        self.threshold_db = ThresholdDatabase()
        
        self.canvas = None
        self.scrollable_frame = None
        self._mousewheel_bound = False
        
    def setup(self):
        """Setup the settings tab UI with scrolling support."""
        restoring_active_preview = self.preview_active
        
        if self._mousewheel_bound:
            try:
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
        
        main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(main_container, bg=Colors.PRIMARY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.PRIMARY_BG)
        
        self._scroll_update_id = None
        self._last_scroll_update = 0
        
        def _update_scroll_region(event=None):
            if self._scroll_update_id:
                self.canvas.after_cancel(self._scroll_update_id)
            
            import time
            current_time = time.time()
            if current_time - self._last_scroll_update < 0.2:
                return
            
            def _do_update():
                try:
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    self._last_scroll_update = time.time()
                except:
                    pass
            
            self._scroll_update_id = self.canvas.after(200, _do_update)
        
        self.scrollable_frame.bind("<Configure>", _update_scroll_region)
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)
        
        self.canvas.bind("<Configure>", _on_canvas_configure)
        
        self._scroll_throttle_id = None
        
        def _on_mousewheel(event):
            if not self.canvas or not self.canvas.winfo_exists():
                return
            
            if self._scroll_throttle_id:
                return
            
            try:
                delta = -1 if event.delta > 0 else 1
                self.canvas.yview_scroll(delta * 2, "units")
                
                self._scroll_throttle_id = self.canvas.after(16, lambda: setattr(self, '_scroll_throttle_id', None))
            except tk.TclError:
                pass
        
        def _bind_mousewheel(event=None):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            self._mousewheel_bound = True
        
        def _unbind_mousewheel(event=None):
            if self._mousewheel_bound:
                try:
                    self.canvas.unbind_all("<MouseWheel>")
                    self._mousewheel_bound = False
                except:
                    pass
        
        self.canvas.bind("<Enter>", _bind_mousewheel)
        self.canvas.bind("<Leave>", _unbind_mousewheel)
        
        _bind_mousewheel()
        
        title_label = tk.Label(
            self.scrollable_frame, 
            text="Model Confidence Settings",
            font=Fonts.SUBTITLE, 
            fg=Colors.WHITE, 
            bg=Colors.PRIMARY_BG
        )
        title_label.pack(pady=(0, 20), fill=tk.X)
        
        self.model_selector = ModelSelector(self.scrollable_frame, self.app)
        self.model_selector.create()
        
        preview_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="Live Camera Preview",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.preview_control_panel = PreviewControlPanel(preview_frame, self)
        self.preview_control_panel.setup()
        
        if restoring_active_preview:
            self.preview_control_panel.enable_stop()
        
        self.preview_container = tk.Frame(preview_frame, bg=Colors.PRIMARY_BG)
        self.preview_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_camera_manager = PreviewCameraManager(self.preview_container)
        self.preview_camera_manager.setup()
        
        if restoring_active_preview:
            self._start_preview_threads()
        
        self.threshold_manager = ThresholdManager(self.scrollable_frame, self.app)
        
        self.threshold_manager.create_model_confidence_section(self.scrollable_frame)
        
        self._load_models_and_create_thresholds()
        
        self.save_button = tk.Button(
            self.scrollable_frame, 
            text="Save Settings", 
            font=Fonts.TEXT_BOLD,
            bg=Colors.SUCCESS, 
            fg=Colors.WHITE, 
            command=self.save_settings
        )
        self.save_button.pack(pady=20, padx=10)
    
    def _load_models_and_create_thresholds(self):
        """Load selected models and create defect threshold sliders."""
        try:
            bf_model_path = self.app.selected_bf_model_path
            od_model_path = self.app.selected_od_model_path
            
            if bf_model_path and od_model_path:
                temp_bf_model = YOLO(bf_model_path)
                temp_od_model = YOLO(od_model_path)
                
                self.threshold_manager.create_defect_thresholds_section(
                    self.scrollable_frame,
                    temp_bf_model,
                    temp_od_model
                )
                
                del temp_bf_model
                del temp_od_model
                
                def _update_scroll():
                    try:
                        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    except:
                        pass
                self.canvas.after(100, _update_scroll)
                
                bf_model_name = self.app.selected_bf_model_name
                od_model_name = self.app.selected_od_model_name
                
                if bf_model_name and bf_model_name != "No Model Available" and od_model_name and od_model_name != "No Model Available":
                    self._load_latest_thresholds_from_db(bf_model_name, od_model_name)
                
            else:
                self._show_no_models_message()
                
        except Exception as e:
            print(f"⚠️ Could not load defect thresholds: {e}")
    
    def _show_no_models_message(self):
        """Show message when no models are available."""
        no_model_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="Defect Thresholds",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        no_model_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        no_model_label = tk.Label(
            no_model_frame,
            text="⚠️ No models available\n\nPlease upload BF and OD models in Model Management tab\nto configure defect thresholds.",
            font=Fonts.TEXT,
            fg="#ffff00",
            bg=Colors.PRIMARY_BG,
            justify=tk.CENTER,
            pady=30
        )
        no_model_label.pack(fill=tk.BOTH, expand=True)
    
    def reload_defect_thresholds_for_selected_models(self):
        """Reload defect threshold sliders when models are changed."""
        try:
            self.threshold_manager.bf_threshold_sliders = {}
            self.threshold_manager.od_threshold_sliders = {}
            self.threshold_manager.bf_size_threshold_sliders = {}
            self.threshold_manager.od_size_threshold_sliders = {}
            self.threshold_manager.bf_threshold_values = {}
            self.threshold_manager.od_threshold_values = {}
            self.threshold_manager.bf_size_threshold_values = {}
            self.threshold_manager.od_size_threshold_values = {}
            
            bf_model_path = self.app.selected_bf_model_path
            od_model_path = self.app.selected_od_model_path
            
            if bf_model_path and od_model_path:
                temp_bf_model = YOLO(bf_model_path)
                temp_od_model = YOLO(od_model_path)
                
                self.threshold_manager.create_defect_thresholds_section(
                    self.scrollable_frame,
                    temp_bf_model,
                    temp_od_model
                )
                
                del temp_bf_model
                del temp_od_model
                
                def _update_scroll():
                    try:
                        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    except:
                        pass
                self.canvas.after(100, _update_scroll)
                
                bf_model_name = self.app.selected_bf_model_name
                od_model_name = self.app.selected_od_model_name
                
                if bf_model_name and bf_model_name != "No Model Available" and od_model_name and od_model_name != "No Model Available":
                    self._load_latest_thresholds_from_db(bf_model_name, od_model_name)
                
            else:
                self._show_no_models_message()
                
        except Exception as e:
            print(f"⚠️ Error reloading defect thresholds: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_latest_thresholds_from_db(self, bf_model_name, od_model_name):
        """Load latest threshold values from database for the selected models. Use defaults if not found."""
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
            
            cursor.execute("""
                SELECT defect_threshold, size_threshold, model_threshold 
                FROM bf_threshold_history 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """, (bf_model_name,))
            bf_result = cursor.fetchone()
            
            if bf_result:
                defect_str, size_str, model_conf = bf_result
                bf_defects = self._parse_defect_string(defect_str)
                bf_sizes = self._parse_size_string(size_str) if size_str else {}
                
                for defect_name, value in bf_defects.items():
                    if defect_name in self.threshold_manager.bf_threshold_sliders:
                        slider, entry, var = self.threshold_manager.bf_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.bf_threshold_values[defect_name] = value
                
                for defect_name, value in bf_sizes.items():
                    if defect_name in self.threshold_manager.bf_size_threshold_sliders:
                        slider, entry, var = self.threshold_manager.bf_size_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.bf_size_threshold_values[defect_name] = value
                
                self.app.bf_conf_threshold = float(model_conf)
                self.app.bf_conf_slider_value.set(float(model_conf) * 100)
                self.threshold_manager.bf_conf_entry.delete(0, tk.END)
                self.threshold_manager.bf_conf_entry.insert(0, str(int(float(model_conf) * 100)))
            cursor.execute("""
                SELECT defect_threshold, size_threshold, model_threshold 
                FROM od_threshold_history 
                WHERE model_name = %s 
                ORDER BY change_timestamp DESC 
                LIMIT 1
            """, (od_model_name,))
            od_result = cursor.fetchone()
            
            if od_result:
                defect_str, size_str, model_conf = od_result
                od_defects = self._parse_defect_string(defect_str)
                od_sizes = self._parse_size_string(size_str) if size_str else {}
                
                for defect_name, value in od_defects.items():
                    if defect_name in self.threshold_manager.od_threshold_sliders:
                        slider, entry, var = self.threshold_manager.od_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.od_threshold_values[defect_name] = value
                
                for defect_name, value in od_sizes.items():
                    if defect_name in self.threshold_manager.od_size_threshold_sliders:
                        slider, entry, var = self.threshold_manager.od_size_threshold_sliders[defect_name]
                        var.set(value)
                        entry.delete(0, tk.END)
                        entry.insert(0, str(int(value)))
                        self.threshold_manager.od_size_threshold_values[defect_name] = value
                
                self.app.od_conf_threshold = float(model_conf)
                self.app.od_conf_slider_value.set(float(model_conf) * 100)
                self.threshold_manager.od_conf_entry.delete(0, tk.END)
                self.threshold_manager.od_conf_entry.insert(0, str(int(float(model_conf) * 100)))
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"⚠️ Could not load thresholds from database: {e}")
    
    def _parse_defect_string(self, defect_str):
        """Parse defect threshold string format: 'rust:80%, dent:60%' to dict."""
        defects = {}
        try:
            pairs = defect_str.split(', ')
            for pair in pairs:
                if ':' in pair:
                    name, value = pair.split(':')
                    value = int(value.replace('%', '').strip())
                    defects[name.strip()] = value
        except Exception as e:
            print(f"⚠️ Error parsing defect string: {e}")
        return defects
    
    def _parse_size_string(self, size_str):
        """Parse size threshold string format: 'rust:1000, dent:5000' to dict (area in pixels)."""
        sizes = {}
        try:
            pairs = size_str.split(', ')
            for pair in pairs:
                if ':' in pair:
                    name, value = pair.split(':')
                    value = int(value.strip())
                    sizes[name.strip()] = value
        except Exception as e:
            print(f"⚠️ Error parsing size string: {e}")
        return sizes
    
    def save_settings(self):
        """Save the current settings to database and apply to inference."""
        confirm = messagebox.askyesno(
            "Confirm Save Settings",
            "Are you sure you want to save the current threshold settings?\n\n"
            "This will update the database and apply settings to the system.",
            icon='question'
        )
        
        if not confirm:
            log_info("settings", "User cancelled save settings")
            return
        
        try:
            log_info("settings", "Saving threshold settings")
            
            employee_id = self.app.current_user if hasattr(self.app, 'current_user') else "unknown"
            
            bf_model_name = self.app.selected_bf_model_name if hasattr(self.app, 'selected_bf_model_name') else "Unknown"
            od_model_name = self.app.selected_od_model_name if hasattr(self.app, 'selected_od_model_name') else "Unknown"
            
            bf_thresholds = self.threshold_manager.get_bf_thresholds()
            od_thresholds = self.threshold_manager.get_od_thresholds()
            bf_size_thresholds = self.threshold_manager.get_bf_size_thresholds()
            od_size_thresholds = self.threshold_manager.get_od_size_thresholds()
            bf_conf = self.threshold_manager.get_bf_model_confidence()
            od_conf = self.threshold_manager.get_od_model_confidence()
            
            self.app.bf_conf_threshold = bf_conf
            self.app.od_conf_threshold = od_conf
            
            bf_success = self.threshold_db.save_bf_thresholds(
                employee_id, 
                bf_thresholds,
                bf_size_thresholds,
                bf_conf, 
                bf_model_name
            )
            
            od_success = self.threshold_db.save_od_thresholds(
                employee_id, 
                od_thresholds,
                od_size_thresholds,
                od_conf, 
                od_model_name
            )
            
            if hasattr(self.app, 'shared_data'):
                self.app.shared_data['od_conf_threshold'] = od_conf
                self.app.shared_data['bf_conf_threshold'] = bf_conf
            
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()
            
            if bf_success and od_success:
                log_info("settings", f"Settings saved successfully by {employee_id}")
                messagebox.showinfo("Settings Saved", 
                                  "Threshold settings have been saved to database successfully.")
            else:
                log_warning("settings", "Partial save - some settings could not be saved")
                messagebox.showwarning("Partial Save", 
                                     "Some settings could not be saved to database.")
        
        except Exception as e:
            log_error("settings", "Failed to save settings", e, {
                "user": getattr(self.app, 'current_user', 'unknown'),
                "bf_model": getattr(self.app, 'selected_bf_model_name', 'Unknown'),
                "od_model": getattr(self.app, 'selected_od_model_name', 'Unknown')
            })
            print(f"❌ Error saving settings: {e}")
            messagebox.showerror("Save Error", f"Failed to save settings:\n{str(e)}")
    
    def start_preview(self):
        """Start the camera preview with model inference."""
        if self.preview_active:
            log_warning("settings", "Attempted to start preview while already running")
            print("Preview already running!")
            return False
        
        log_info("settings", "Starting camera preview")
        
        models_ok, models_error = self._check_models_available()
        if not models_ok:
            log_warning("settings", f"Models check failed: {models_error}")
            messagebox.showerror("Models Check Failed", models_error)
            return False
        
        plc_ok, plc_error = self._check_plc_connection()
        if not plc_ok:
            log_warning("settings", f"PLC check failed: {plc_error}")
            messagebox.showerror("PLC Check Failed", plc_error)
            return False
        
        cameras_ok, cameras_error = self._check_cameras_connected()
        if not cameras_ok:
            log_warning("settings", f"Camera check failed: {cameras_error}")
            messagebox.showerror("Camera Check Failed", cameras_error)
            return False
        
        selected_models = self.model_selector.get_selected_models()
        bf_model_path = selected_models['bf_model_path']
        od_model_path = selected_models['od_model_path']
        
        if not bf_model_path or not od_model_path:
            log_warning("settings", "Models not available for preview")
            messagebox.showerror(
                "Models Not Available", 
                "⚠️ Cannot start preview\n\n"
                "Both BF and OD models are required.\n\n"
                "Please upload models in the Model Management tab first."
            )
            return False
        
        self.preview_stop_flag = ThreadStopFlag()
        
        if not hasattr(self.app, 'inspection_running') or not self.app.inspection_running:
            self._start_camera_capture_processes()
        
        try:
            log_info("settings", f"Loading models - BF: {bf_model_path}, OD: {od_model_path}")
            self.preview_bf_model = YOLO(bf_model_path)
            if torch.cuda.is_available():
                self.preview_bf_model.to("cuda")
            
            self.preview_od_model = YOLO(od_model_path)
            if torch.cuda.is_available():
                self.preview_od_model.to("cuda")
            
            log_info("settings", "Models loaded successfully")
                
        except Exception as e:
            log_error("settings", "Failed to load models for preview", e, {
                "bf_model_path": bf_model_path,
                "od_model_path": od_model_path
            })
            messagebox.showerror("Model Load Error", f"Failed to load models:\n{str(e)}")
            print(f"❌ Error loading models: {e}")
            return False
        
        self._save_threshold_snapshot()
        
        plc_client = snap7.client.Client()
        plc_client.connect("172.17.8.17", 0, 1)        
        data = plc_client.read_area(Areas.DB, 86, 0, 2)
        set_bool(data, byte_index=1, bool_index=6, value=True)
        set_bool(data, byte_index=1, bool_index=7, value=True)
        plc_client.write_area(Areas.DB, 86, 0, data)
        plc_client.disconnect()

        self.preview_active = True
        
        self._block_navigation_buttons()
        
        self._block_logout_button()
        
        self._block_model_dropdowns()
        self._block_save_button()
        
        if hasattr(self.app, 'protocol'):
            self.app.protocol("WM_DELETE_WINDOW", self._block_closing)
        
        self._start_preview_threads()
        
        self._monitor_preview_errors()
        
        return True
    
    def stop_preview(self):
        """Stop the camera preview with save/discard option and proper cleanup."""
        try:
            log_info("settings", "Attempting to stop camera preview")
            
            if not self.preview_active:
                log_warning("settings", "Stop preview called but preview is not running")
                print("Preview is not running.")
                return
            
            if self._thresholds_changed():
                log_info("settings", "Thresholds were modified - prompting user to save changes")
                response = messagebox.askyesnocancel(
                    "Save Threshold Changes?",
                    "Threshold values have been modified.\n\n"
                    "Do you want to save these changes to the database?\n\n"
                    "Yes: Save changes\n"
                    "No: Discard changes (restore previous values)\n"
                    "Cancel: Continue preview"
                )
                
                if response is None:
                    log_info("settings", "User cancelled stop preview - continuing preview")
                    return
                elif response:
                    log_info("settings", "User chose to save threshold changes")
                    self.save_settings()
                else:
                    log_info("settings", "User chose to discard threshold changes")
                    self._restore_threshold_snapshot()
            
            log_info("settings", "Turning off PLC lights")
            plc_client = snap7.client.Client()
            plc_client.connect("172.17.8.17", 0, 1)        
            data = plc_client.read_area(Areas.DB, 86, 0, 2)
            set_bool(data, byte_index=1, bool_index=6, value=False)
            set_bool(data, byte_index=1, bool_index=7, value=False)
            plc_client.write_area(Areas.DB, 86, 0, data)
            plc_client.disconnect()
            
            self.preview_active = False
            
            if self.preview_stop_flag:
                self.preview_stop_flag.set()
            
            self._unblock_navigation_buttons()
            
            self._unblock_logout_button()
            
            self._unblock_model_dropdowns()
            self._unblock_save_button()
            
            if hasattr(self.app, 'on_closing'):
                self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
            
            self._display_black_screens()

            if hasattr(self, 'preview_od_thread') and self.preview_od_thread and self.preview_od_thread.is_alive():
                self.preview_od_thread.join(timeout=2.0)
            
            if hasattr(self, 'preview_bf_thread') and self.preview_bf_thread and self.preview_bf_thread.is_alive():
                self.preview_bf_thread.join(timeout=2.0)
            
            if self.preview_bf_model is not None:
                del self.preview_bf_model
                self.preview_bf_model = None
            
            if self.preview_od_model is not None:
                del self.preview_od_model
                self.preview_od_model = None
            
            if self.preview_bf_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
            
            if self.preview_od_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_od_camera_process)
            
            self.app.process_manager.stop_all_preview()
            
            log_info("settings", "Camera preview stopped successfully")
            
        except Exception as e:
            log_error("settings", "Error stopping camera preview", e)
            messagebox.showerror("Error", f"Failed to stop preview:\n{str(e)}")
        
        self.preview_bf_camera_process = None
        self.preview_od_camera_process = None
        
        if self.preview_camera_manager:
            for feed_id in ['bf', 'od']:
                feed = self.preview_camera_manager.get_feed(feed_id)
                if feed and hasattr(feed, 'cleanup'):
                    feed.cleanup()
        
        self.app.process_manager.cleanup_gpu_memory()
        
        import gc
        gc.collect()
        
        time.sleep(0.3)
        
    
    def _start_camera_capture_processes(self):
        """Start camera capture processes for preview mode."""
        try:
            self.preview_bf_camera_process = Process(
                target=capture_frames_bigface,
                args=(self.app.shared_frame_bigface, self.app.frame_lock_bigface, self.app.frame_shape, self.app.shared_data),
                daemon=True
            )
            self.preview_bf_camera_process.start()
            
            self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
            
            self.preview_od_camera_process = Process(
                target=capture_frames_od,
                args=(self.app.shared_frame_od, self.app.frame_lock_od, self.app.frame_shape, self.app.shared_data),
                daemon=True
            )
            self.preview_od_camera_process.start()
            
            self.app.process_manager.register_preview_process(self.preview_od_camera_process)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error starting camera capture: {e}")
            messagebox.showerror("Camera Error", f"Failed to start camera capture:\n{str(e)}")
    
    def _start_preview_threads(self):
        """Start camera feed update threads for preview."""
        self.preview_stop_flag.clear()
        
        self.preview_od_thread = threading.Thread(target=self._update_od_preview, name="Preview_OD_Thread")
        self.preview_od_thread.daemon = True
        self.preview_od_thread.start()
        
        self.app.process_manager.register_preview_thread(self.preview_od_thread)
        
        self.preview_bf_thread = threading.Thread(target=self._update_bf_preview, name="Preview_BF_Thread")
        self.preview_bf_thread.daemon = True
        self.preview_bf_thread.start()
        
        self.app.process_manager.register_preview_thread(self.preview_bf_thread)
    
    def _filter_and_draw_detections(self, frame, results, model_conf_threshold, defect_thresholds, size_thresholds, model_type='od'):
        """
        Filter detections based on confidence and size thresholds, then draw annotations.
        Uses different colors for different classes and bold text for class names.
        
        Args:
            frame: Original frame
            results: YOLO prediction results
            model_conf_threshold: Model confidence threshold (0-1)
            defect_thresholds: Dictionary of defect-specific confidence thresholds (0-100)
            size_thresholds: Dictionary of defect-specific size thresholds (area in px²)
            model_type: 'od' or 'bf' to identify which defect thresholds to use
            
        Returns:
            Annotated frame with filtered detections
        """
        color_palette = [
            (0, 255, 0),
            (255, 0, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
            (128, 0, 128),
            (0, 128, 255),
            (128, 128, 0),
            (255, 128, 0),
            (0, 128, 128),
            (128, 0, 255),
        ]
        
        annotated_frame = frame.copy()
        
        boxes = results[0].boxes
        
        if boxes is None or len(boxes) == 0:
            return annotated_frame
        
        class_names = results[0].names
        
        for box in boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            class_name = class_names[cls_id]
            
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            width = x2 - x1
            height = y2 - y1
            bbox_area = width * height
            
            defect_threshold = defect_thresholds.get(class_name, 0) / 100.0
            
            size_threshold = size_thresholds.get(class_name, 0)
            
            if conf >= model_conf_threshold and conf >= defect_threshold and bbox_area >= size_threshold:
                color = color_palette[cls_id % len(color_palette)]
                
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
                
                label = f"{class_name} {conf:.2f}"
                
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                
                label_y1 = max(y1 - label_height - baseline - 10, 0)
                label_y2 = max(y1, label_height + baseline + 10)
                
                cv2.rectangle(
                    annotated_frame,
                    (x1, label_y1),
                    (x1 + label_width + 10, label_y2),
                    color,
                    -1
                )
                
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1 + 5, label_y2 - baseline - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )
        
        return annotated_frame
    
    def _update_od_preview(self):
        """Update OD camera preview feed with model inference."""
        od_feed = self.preview_camera_manager.get_feed('od') if self.preview_camera_manager else None
        
        while od_feed and od_feed.canvas and od_feed.canvas.winfo_exists() and not self.preview_stop_flag.is_set():
            try:
                if self.preview_active:
                    with self.app.frame_lock_od:
                        np_frame = np.frombuffer(
                            self.app.shared_frame_od.get_obj(), 
                            dtype=np.uint8
                        ).reshape(self.app.frame_shape)
                        frame = np_frame.copy()
        
                    current_od_conf = self.app.od_conf_slider_value.get() / 100.0
                    current_od_defect_thresholds = self.threshold_manager.get_od_thresholds()
                    current_od_size_thresholds = self.threshold_manager.get_od_size_thresholds()
                    
                    if self.preview_od_model is None:
                        black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                        od_feed.update_frame(black_frame)
                        time.sleep(0.03)
                        continue
                    
                    results = self.preview_od_model.predict(
                        frame, 
                        device=0 if torch.cuda.is_available() else 'cpu',
                        conf=0.01,
                        verbose=False,
                        half=True if torch.cuda.is_available() else False
                    )
                    
                    annotated_frame = self._filter_and_draw_detections(
                        frame, 
                        results, 
                        current_od_conf, 
                        current_od_defect_thresholds,
                        current_od_size_thresholds,
                        model_type='od'
                    )
                    od_feed.update_frame(annotated_frame)
                else:
                    black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                    od_feed.update_frame(black_frame)
                
                    time.sleep(0.03)
                
            except Exception as e:
                print(f"❌ OD preview thread error: {e}")
                import traceback
                traceback.print_exc()
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['system_error'] = True
                break
        
    def _update_bf_preview(self):
        """Update Bigface camera preview feed with model inference."""
        bf_feed = self.preview_camera_manager.get_feed('bf') if self.preview_camera_manager else None
        
        while bf_feed and bf_feed.canvas and bf_feed.canvas.winfo_exists() and not self.preview_stop_flag.is_set():
            try:
                if self.preview_active:
                    with self.app.frame_lock_bigface:
                        np_frame = np.frombuffer(
                            self.app.shared_frame_bigface.get_obj(), 
                            dtype=np.uint8
                        ).reshape(self.app.frame_shape)
                        frame = np_frame.copy()
                    
                    current_bf_conf = self.app.bf_conf_slider_value.get() / 100.0
                    current_bf_defect_thresholds = self.threshold_manager.get_bf_thresholds()
                    current_bf_size_thresholds = self.threshold_manager.get_bf_size_thresholds()
                    
                    if self.preview_bf_model is None:
                        black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                        bf_feed.update_frame(black_frame)
                        time.sleep(0.03)
                        continue
                    
                    results = self.preview_bf_model.predict(
                        frame, 
                        device=0 if torch.cuda.is_available() else 'cpu',
                        conf=0.01,
                        verbose=False,
                        half=True if torch.cuda.is_available() else False
                    )
                    
                    annotated_frame = self._filter_and_draw_detections(
                        frame, 
                        results, 
                        current_bf_conf, 
                        current_bf_defect_thresholds,
                        current_bf_size_thresholds,
                        model_type='bf'
                    )
                    
                    bf_feed.update_frame(annotated_frame)
                else:
                    black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
                    bf_feed.update_frame(black_frame)
                
                    time.sleep(0.03)
                
            except Exception as e:
                print(f"❌ BF preview thread error: {e}")
                import traceback
                traceback.print_exc()
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['system_error'] = True
                break

    def _display_black_screens(self):
        """Display black screens on both camera feeds when preview is stopped."""
        black_frame = np.zeros(self.app.frame_shape, dtype=np.uint8)
        
        od_feed = self.preview_camera_manager.get_feed('od')
        od_feed.update_frame(black_frame)
        
        bf_feed = self.preview_camera_manager.get_feed('bf')
        bf_feed.update_frame(black_frame)
    
    def _block_navigation_buttons(self):
        """Block Inference and System Check navigation buttons with red color."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            if 'inference' in navbar.buttons:
                navbar.buttons['inference'].button.config(
                    state=tk.DISABLED,
                    bg=Colors.DANGER,
                    disabledforeground=Colors.WHITE
                )
            
            if 'system_check' in navbar.buttons:
                navbar.buttons['system_check'].button.config(
                    state=tk.DISABLED,
                    bg=Colors.DANGER,
                    disabledforeground=Colors.WHITE
                )
            
    
    def _unblock_navigation_buttons(self):
        """Unblock Inference and System Check navigation buttons."""
        if hasattr(self.app, 'navbar_manager') and self.app.navbar_manager:
            navbar = self.app.navbar_manager
            
            if 'inference' in navbar.buttons:
                nav_button = navbar.buttons['inference']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
            
            if 'system_check' in navbar.buttons:
                nav_button = navbar.buttons['system_check']
                nav_button.button.config(
                    state=tk.NORMAL,
                    bg=nav_button.inactive_bg
                )
    
    def _block_logout_button(self):
        """Block the logout button during preview with grey color."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.DISABLED,
                bg="#6c757d",
                fg=Colors.WHITE
            )
    
    def _unblock_logout_button(self):
        """Unblock the logout button after preview with red color."""
        if hasattr(self.app, 'logout_button') and self.app.logout_button:
            self.app.logout_button.config(
                state=tk.NORMAL,
                bg=Colors.DANGER,
                fg=Colors.WHITE
            )
    
    def _block_save_button(self):
        """Block the Save Settings button during preview with red color."""
        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.config(
                state=tk.DISABLED,
                bg=Colors.DANGER,
                disabledforeground=Colors.WHITE
            )
    
    def _unblock_save_button(self):
        """Unblock the Save Settings button after preview."""
        if hasattr(self, 'save_button') and self.save_button:
            self.save_button.config(
                state=tk.NORMAL,
                bg=Colors.SUCCESS
            )
    
    def _block_model_dropdowns(self):
        """Block model dropdown selection during preview."""
        if self.model_selector:
            if self.model_selector.bf_model_dropdown:
                self.model_selector.bf_model_dropdown.config(state=tk.DISABLED)
            if self.model_selector.od_model_dropdown:
                self.model_selector.od_model_dropdown.config(state=tk.DISABLED)
    
    def _unblock_model_dropdowns(self):
        """Unblock model dropdown selection after preview."""
        if self.model_selector:
            if self.model_selector.bf_model_dropdown:
                self.model_selector.bf_model_dropdown.config(state="readonly")
            if self.model_selector.od_model_dropdown:
                self.model_selector.od_model_dropdown.config(state="readonly")
    def _save_threshold_snapshot(self):
        """Save current threshold values to memory for potential restore."""
        if self.threshold_manager:
            self.threshold_snapshot = {
                'bf_thresholds': self.threshold_manager.get_bf_thresholds(),
                'od_thresholds': self.threshold_manager.get_od_thresholds(),
                'bf_size_thresholds': self.threshold_manager.get_bf_size_thresholds(),
                'od_size_thresholds': self.threshold_manager.get_od_size_thresholds(),
                'bf_conf': self.threshold_manager.get_bf_model_confidence(),
                'od_conf': self.threshold_manager.get_od_model_confidence()
            }
    
    def _restore_threshold_snapshot(self):
        """Restore threshold values from snapshot."""
        if self.threshold_snapshot and self.threshold_manager:
            self.threshold_manager.restore_thresholds(
                self.threshold_snapshot['bf_thresholds'],
                self.threshold_snapshot['od_thresholds'],
                self.threshold_snapshot['bf_conf'],
                self.threshold_snapshot['od_conf'],
                self.threshold_snapshot.get('bf_size_thresholds'),
                self.threshold_snapshot.get('od_size_thresholds')
            )
    
    def _thresholds_changed(self):
        """Check if threshold values have changed since snapshot."""
        if not self.threshold_snapshot or not self.threshold_manager:
            return False
        
        current_bf = self.threshold_manager.get_bf_thresholds()
        current_od = self.threshold_manager.get_od_thresholds()
        current_bf_size = self.threshold_manager.get_bf_size_thresholds()
        current_od_size = self.threshold_manager.get_od_size_thresholds()
        current_bf_conf = self.threshold_manager.get_bf_model_confidence()
        current_od_conf = self.threshold_manager.get_od_model_confidence()
        
        bf_changed = current_bf != self.threshold_snapshot['bf_thresholds']
        od_changed = current_od != self.threshold_snapshot['od_thresholds']
        bf_size_changed = current_bf_size != self.threshold_snapshot.get('bf_size_thresholds', {})
        od_size_changed = current_od_size != self.threshold_snapshot.get('od_size_thresholds', {})
        bf_conf_changed = abs(current_bf_conf - self.threshold_snapshot['bf_conf']) > 0.001
        od_conf_changed = abs(current_od_conf - self.threshold_snapshot['od_conf']) > 0.001
        
        return bf_changed or od_changed or bf_size_changed or od_size_changed or bf_conf_changed or od_conf_changed
    
    def _block_closing(self):
        """Block app closing when preview is running."""
        messagebox.showwarning(
            "Preview Running",
            "Camera preview is currently running!\n\n"
            "Please stop the preview before closing the application."
        )
    
    def _monitor_preview_errors(self):
        """Monitor for system errors during preview mode."""
        if not self.preview_active:
            return
        
        if hasattr(self.app, 'shared_data') and self.app.shared_data:
            if self.app.shared_data.get('system_error', False):
                self.app.shared_data['system_error'] = False
                
                self._show_preview_error_popup()
                return
        
        if self.preview_active:
            try:
                self.parent.after(500, self._monitor_preview_errors)
            except:
                pass
    
    def _show_preview_error_popup(self):
        """Show error popup and force stop preview."""
        from tkinter import messagebox
        
        try:
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
            
            self.preview_active = False
            
            if self.preview_stop_flag:
                self.preview_stop_flag.set()
            
            if self.preview_bf_model is not None:
                del self.preview_bf_model
                self.preview_bf_model = None
            
            if self.preview_od_model is not None:
                del self.preview_od_model
                self.preview_od_model = None
            
            if self.preview_bf_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
            
            if self.preview_od_camera_process is not None:
                self.app.process_manager.register_preview_process(self.preview_od_camera_process)
            
            self.app.process_manager.stop_all_preview()
            
            self.preview_bf_camera_process = None
            self.preview_od_camera_process = None
            
            self._unblock_navigation_buttons()
            self._unblock_logout_button()
            self._unblock_model_dropdowns()
            self._unblock_save_button()
            
            if self.preview_control_panel:
                self.preview_control_panel.enable_start()
            
            if hasattr(self.app, 'on_closing'):
                self.app.protocol("WM_DELETE_WINDOW", self.app.on_closing)
            
            self._display_black_screens()
            
            self.app.process_manager.cleanup_gpu_memory()
            
        except Exception as e:
            print(f"❌ Error during preview emergency stop: {e}")
        
        messagebox.showerror(
            "Preview Error Detected",
            "⚠️ A critical error occurred during preview!\n\n"
            "The preview has been stopped automatically.\n\n"
            "Possible causes:\n"
            "• Camera disconnection\n"
            "• PLC communication error\n"
            "• GPU memory overflow\n"
            "• Model inference failure\n\n"
            "Recommended action:\n"
            "Please check camera and PLC connections.\n"
            "Restart the application if the issue persists.\n\n"
            "Click OK to continue using other features."
        )
    
    def _check_models_available(self):
        """
        Check if both BF and OD models are available.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        bf_model_path = getattr(self.app, 'selected_bf_model_path', None)
        od_model_path = getattr(self.app, 'selected_od_model_path', None)
        
        if not bf_model_path or not od_model_path:
            return False, "⚠️ Models Not Available\n\nBoth BF and OD models are required.\n\nPlease upload models in Model Management tab first."
        
        import os
        if not os.path.exists(bf_model_path):
            return False, f"⚠️ BF Model File Not Found\n\nPath: {bf_model_path}\n\nPlease upload the model again."
        
        if not os.path.exists(od_model_path):
            return False, f"⚠️ OD Model File Not Found\n\nPath: {od_model_path}\n\nPlease upload the model again."
        
        return True, ""
    
    def _check_plc_connection(self):
        """
        Check PLC connection.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        try:
            import snap7
            from snap7.type import Areas
            
            plc = snap7.client.Client()
            plc.connect(AppConfig.PLC_IP, AppConfig.PLC_RACK, AppConfig.PLC_SLOT)
            
            if plc.get_connected():
                plc.disconnect()
                return True, ""
            else:
                return False, f"⚠️ PLC Not Connected\n\nCannot connect to PLC at {AppConfig.PLC_IP}\n\nPlease check:\n• PLC is powered on\n• Network cable is connected\n• IP address is correct"
        
        except Exception as e:
            return False, f"⚠️ PLC Connection Failed\n\nError: {str(e)}\n\nPlease check PLC connection and network settings."
    
    def _check_cameras_connected(self):
        """
        Check if cameras are connected.
        
        Returns:
            tuple: (bool, str) - (success, error_message)
        """
        import cv2
        cameras_connected = []
        
        for idx in [0, 1]:
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                cameras_connected.append(idx)
                cap.release()
        
        if len(cameras_connected) < 2:
            return False, f"⚠️ Cameras Not Connected\n\nRequired: 2 cameras\nDetected: {len(cameras_connected)} camera(s)\n\nPlease connect all cameras and try again."
        
        return True, ""
    
    def capture_bf_frame(self):
        """Capture current BF frame and save to disk."""
        if not self.preview_active:
            messagebox.showwarning("Preview Not Active", "Please start the preview first before capturing frames.")
            return
        
        try:
            from datetime import datetime
            import os
            
            with self.app.frame_lock_bigface:
                np_frame = np.frombuffer(
                    self.app.shared_frame_bigface.get_obj(), 
                    dtype=np.uint8
                ).reshape(self.app.frame_shape)
                frame = np_frame.copy()
            
            username = os.getlogin()
            save_path = f"C:\\Users\\{username}\\Desktop\\Settings Frame\\BF"
            os.makedirs(save_path, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(save_path, filename)
            
            cv2.imwrite(filepath, frame)
            
            messagebox.showinfo(
                "Frame Captured",
                f"✅ BF frame captured successfully!\n\n"
                f"Saved to:\n{filepath}"
            )
            
        except Exception as e:
            print(f"❌ Error capturing BF frame: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Capture Error", f"Failed to capture BF frame:\n{str(e)}")
    
    def capture_od_frame(self):
        """Capture current OD frame and save to disk."""
        if not self.preview_active:
            messagebox.showwarning("Preview Not Active", "Please start the preview first before capturing frames.")
            return
        
        try:
            from datetime import datetime
            import os
            
            with self.app.frame_lock_od:
                np_frame = np.frombuffer(
                    self.app.shared_frame_od.get_obj(), 
                    dtype=np.uint8
                ).reshape(self.app.frame_shape)
                frame = np_frame.copy()
            
            username = os.getlogin()
            save_path = f"C:\\Users\\{username}\\Desktop\\Settings Frame\\OD"
            os.makedirs(save_path, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(save_path, filename)
            
            cv2.imwrite(filepath, frame)
            
            messagebox.showinfo(
                "Frame Captured",
                f"✅ OD frame captured successfully!\n\n"
                f"Saved to:\n{filepath}"
            )
            
        except Exception as e:
            print(f"❌ Error capturing OD frame: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Capture Error", f"Failed to capture OD frame:\n{str(e)}")
    
    def cleanup(self):
        """Cleanup method called when settings tab is destroyed."""
        if self._mousewheel_bound:
            try:
                self.canvas.unbind_all("<MouseWheel>")
                self._mousewheel_bound = False
            except:
                pass
        
        if self.preview_active:
            try:
                if self.preview_stop_flag:
                    self.preview_stop_flag.set()
                
                self.preview_active = False
                
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
                
                if self.preview_bf_model is not None:
                    del self.preview_bf_model
                    self.preview_bf_model = None
                
                if self.preview_od_model is not None:
                    del self.preview_od_model
                    self.preview_od_model = None
                
                if self.preview_bf_camera_process is not None:
                    self.app.process_manager.register_preview_process(self.preview_bf_camera_process)
                
                if self.preview_od_camera_process is not None:
                    self.app.process_manager.register_preview_process(self.preview_od_camera_process)
                
                self.app.process_manager.stop_all_preview()
                
                self.preview_bf_camera_process = None
                self.preview_od_camera_process = None
                
                self.app.process_manager.cleanup_gpu_memory()
                
            except Exception as e:
                print(f"⚠️ Error during preview cleanup: {e}")            