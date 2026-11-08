"""
Inference Tab UI Component
Modularized layout with status panel, camera feeds, results, and roller info
"""

import tkinter as tk
import numpy as np
import time
import threading
from ..utils.styles import Colors
from ..utils.config import AppConfig
from ..utils.debug_logger import log_error, log_warning, log_info
from .status_panel import StatusPanel
from .camera_feed import CameraFeedManager
from .control_panel import ControlPanel
from .results_panel import ResultsPanel
from .roller_info_panel import RollerInfoPanel


class InferenceTab:
    """Inference tab for real-time inspection display and control."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the inference tab.
        
        Args:
            parent: Parent frame (tab)
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.status_panel = None
        self.camera_manager = None
        self.control_panel = None
        self.results_panel = None
        self.roller_info_panel = None
        
    def setup(self):
        """Setup the inference tab UI in a single-frame layout."""
        try:
            log_info("inference", "Setting up Inference tab UI")
            
            main_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
            main_container.pack(fill=tk.BOTH, expand=True)
            
            self.status_panel = StatusPanel(main_container, self.app)
            self.status_panel.create()
            
            self._monitor_status_updates()
            
            middle_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
            middle_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.camera_manager = CameraFeedManager(middle_frame)
            self.camera_manager.setup()
            
            bottom_frame = tk.Frame(main_container, bg=Colors.PRIMARY_BG)
            bottom_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self.results_panel = ResultsPanel(bottom_frame, self.app)
            self.results_panel.create()
            
            self.control_panel = ControlPanel(bottom_frame, self.app)
            self.control_panel.setup()
            
            log_info("inference", "Inference tab setup completed successfully")
            
        except Exception as e:
            log_error("inference", "Failed to setup Inference tab", e)
            raise
    
    def update_od_camera(self):
        """Update OD camera feed display."""
        od_feed = self.camera_manager.get_feed('od')
        
        frame_delay = 0.025
        
        while not self.app.camera_stop_flag.is_set():
            try:
                if od_feed is None or od_feed.canvas is None:
                    break
                
                inspection_running = (
                    hasattr(self.app, 'processes') and 
                    self.app.processes is not None and 
                    len(self.app.processes) > 0 and
                    self.app.inspection_running
                )
                
                if inspection_running:
                    with self.app.annotated_frame_lock_od:
                        np_frame = np.frombuffer(
                            self.app.shared_annotated_od.get_obj(), 
                            dtype=np.uint8
                        ).reshape(self.app.frame_shape)
                        frame = np_frame.copy()
                else:
                    frame = np.zeros(self.app.frame_shape, dtype=np.uint8)


                od_feed.update_frame(frame)
                
                time.sleep(frame_delay)
            except Exception as e:
                error_msg = f"OD camera thread error: {e}"
                print(error_msg)
                log_error("inference", "OD camera update failed", e, {
                    "camera_id": "OD",
                    "inspection_running": getattr(self.app, 'inspection_running', False)
                })
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['system_error'] = True
                break

    def update_bf_camera(self):
        """Update Bigface camera feed display."""
        bf_feed = self.camera_manager.get_feed('bf')
        
        frame_delay = 0.025
        
        while not self.app.camera_stop_flag.is_set():
            try:
                if bf_feed is None or bf_feed.canvas is None:
                    break
                
                inspection_running = (
                    hasattr(self.app, 'processes') and 
                    self.app.processes is not None and 
                    len(self.app.processes) > 0 and
                    self.app.inspection_running
                )
                
                if inspection_running:
                    with self.app.annotated_frame_lock_bigface:
                        np_frame = np.frombuffer(
                            self.app.shared_annotated_bigface.get_obj(), 
                            dtype=np.uint8
                        ).reshape(self.app.frame_shape)
                        frame = np_frame.copy()
                else:
                    frame = np.zeros(self.app.frame_shape, dtype=np.uint8)

                bf_feed.update_frame(frame)
                
                time.sleep(frame_delay)
            except Exception as e:
                error_msg = f"BF camera thread error: {e}"
                print(error_msg)
                log_error("inference", "BF camera update failed", e, {
                    "camera_id": "BF",
                    "inspection_running": getattr(self.app, 'inspection_running', False)
                })
                if hasattr(self.app, 'shared_data') and self.app.shared_data:
                    self.app.shared_data['system_error'] = True
                break
    
    def start_camera_threads(self):
        """Start camera feed update threads."""
        try:
            log_info("inference", "Starting camera feed threads")
            
            self.app.camera_stop_flag.clear()
            
            self.app.od_thread = threading.Thread(target=self.update_od_camera, name="OD_Camera_Thread")
            self.app.od_thread.daemon = True
            self.app.od_thread.start()
            
            self.app.process_manager.register_inference_thread(self.app.od_thread)
            
            self.app.bf_thread = threading.Thread(target=self.update_bf_camera, name="BF_Camera_Thread")
            self.app.bf_thread.daemon = True
            self.app.bf_thread.start()
            
            self.app.process_manager.register_inference_thread(self.app.bf_thread)
            
            log_info("inference", "Camera feed threads started successfully")
            
        except Exception as e:
            log_error("inference", "Failed to start camera threads", e)
            raise
    
    def _monitor_status_updates(self):
        """Monitor shared_data for status updates and update status panel."""
        try:
            if hasattr(self.app, 'shared_data') and self.app.shared_data and self.status_panel:
                system_ready = self.app.shared_data.get('system_ready', False)
                
                if system_ready:
                    
                    system_mode = self.app.shared_data.get('system_mode', False)
                    if system_mode:
                        self.status_panel.update_machine_mode("AUTO", "#00ff00")
                    else:
                        self.status_panel.update_machine_mode("MANUAL", "#ff0000")
                    
                    disc_status = self.app.shared_data.get('disc_status', False)
                    if disc_status:
                        self.status_panel.update_disc_status("READY", "#00ff00")
                    else:
                        self.status_panel.update_disc_status("NOT READY", "#ff0000")
                else:
                    self.status_panel.update_machine_mode("Not Available", "#ffff00")
                    self.status_panel.update_disc_status("Not Available", "#ffff00")
                
                if self.results_panel:
                    self.results_panel.update_from_shared_data(self.app.shared_data)
                
                if self.status_panel and not hasattr(self, '_model_update_counter'):
                    self._model_update_counter = 0
                
                if hasattr(self, '_model_update_counter'):
                    self._model_update_counter += 1
                    if self._model_update_counter >= 10:
                        self.status_panel.update_model_names()
                        self._model_update_counter = 0
            
            if hasattr(self.app, 'roller_data_updated') and self.app.roller_data_updated:
                if self.status_panel and hasattr(self.status_panel, 'refresh_roller_list'):
                    self.status_panel.refresh_roller_list()
                self.app.roller_data_updated = False
        except:
            pass
        
        try:
            self.parent.after(500, self._monitor_status_updates)
        except:
            pass
