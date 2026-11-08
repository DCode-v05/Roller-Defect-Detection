"""
System Information Component
Displays system status and hardware information
"""

import tkinter as tk
from tkinter import messagebox
import cv2
import snap7
from snap7.type import Areas
from ..utils.styles import Colors, Fonts


class SystemInformation:
    """Component for displaying system information."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the system information component.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        
        self.info_text = None
    
    def create(self):
        """Create the system information UI."""
        main_frame = tk.LabelFrame(
            self.parent,
            text="System Information",
            font=Fonts.HEADER,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        buttons_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            buttons_frame,
            text="� Refresh System",
            font=Fonts.TEXT_BOLD,
            bg="#007BFF",
            fg=Colors.WHITE,
            activebackground="#0056b3",
            activeforeground=Colors.WHITE,
            command=self.refresh_system,
            width=20,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        text_frame = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.info_text = tk.Text(
            text_frame,
            font=("Consolas", 9),
            bg="#1E1E1E",
            fg="#00FF00",
            insertbackground=Colors.WHITE,
            yscrollcommand=scrollbar.set,
            height=12,
            wrap=tk.WORD
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.info_text.yview)
        
        self.load_system_info()
    
    def load_system_info(self):
        """Load and display system information."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        try:
            plc_status, plc_connected = self._check_plc_connection()
            
            camera_status, cameras_connected = self._check_cameras()
            
            connected_devices = (1 if plc_connected else 0) + cameras_connected
            total_devices = 3
            
            if connected_devices == total_devices:
                system_ready = f"✅ Yes - All devices connected: {connected_devices}/{total_devices}"
            else:
                system_ready = f"❌ No - Some devices missing: {connected_devices}/{total_devices}"
            
            info = f"""PLC Connection: {plc_status}
{camera_status}

PLC DETAILS:
PLC IP: 172.17.8.17
Rack: 0
Slot: 1
DB Number: 86

System Ready: {system_ready}
"""
            
            self.info_text.insert(tk.END, info)
            
        except Exception as e:
            self.info_text.insert(tk.END, f"Error loading system info:\n{str(e)}")
        
        self.info_text.config(state=tk.DISABLED)
    
    def _check_plc_connection(self):
        """
        Check PLC connection status.
        
        Returns:
            tuple: (status_text, is_connected)
        """
        try:
            plc_client = snap7.client.Client()
            plc_client.connect("172.17.8.17", 0, 1)
            
            data = plc_client.read_area(Areas.DB, 86, 0, 1)
            plc_client.disconnect()
            
            return "✅ Connected", True
        
        except Exception as e:
            return "❌ Disconnected", False
    
    def _check_cameras(self):
        """
        Check camera connections.
        Checks camera indices 0 and 1.
        
        Returns:
            tuple: (status_text, number_of_connected_cameras)
        """
        connected_cameras = 0
        camera_indices = [0, 1]
        
        for index in camera_indices:
            try:
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        connected_cameras += 1
                    cap.release()
            except:
                pass
        
        if connected_cameras == 2:
            status = "Cameras: ✅ Both cameras connected (2/2)"
        elif connected_cameras == 1:
            status = "Cameras: ⚠️ One camera disconnected (1/2)"
        else:
            status = "Cameras: ❌ Both cameras disconnected (0/2)"
        
        return status, connected_cameras
    
    def refresh_system(self):
        """Refresh system status information."""
        try:
            self.load_system_info()
            messagebox.showinfo("Success", "System status refreshed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh system:\n{str(e)}")
