"""
Preview Camera Feed Component for Settings Tab
Displays live camera feeds for settings preview
"""

import tkinter as tk
import cv2
import PIL.Image
import PIL.ImageTk
import numpy as np
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig


class PreviewCameraFeed:
    """Component for displaying a single camera feed in preview mode."""
    
    def __init__(self, parent, title, canvas_id):
        """
        Initialize a camera feed display.
        
        Args:
            parent: Parent frame
            title: Camera title (e.g., "Camera 1 - OD")
            canvas_id: Identifier for this camera (e.g., "od" or "bf")
        """
        self.parent = parent
        self.title = title
        self.canvas_id = canvas_id
        self.canvas = None
        self.camera_frame = None
        self._last_update_time = 0
        self._frame_skip_counter = 0
        self._image_id = None
        
    def create(self, row, column):
        """
        Create the camera feed UI.
        
        Args:
            row: Grid row position
            column: Grid column position
        """
        self.camera_frame = tk.LabelFrame(
            self.parent,
            text=self.title,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=0,
            highlightthickness=0
        )
        self.camera_frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
        
        self.canvas = tk.Canvas(
            self.camera_frame,
            bg=Colors.BLACK,
            width=AppConfig.CAMERA_WIDTH,
            height=AppConfig.CAMERA_HEIGHT,
            highlightthickness=0
        )
        self.canvas.pack(padx=5, pady=5)
        
        return self.camera_frame
    
    def update_frame(self, frame):
        """
        Update the displayed frame with memory leak prevention.
        
        Args:
            frame: OpenCV frame (BGR format)
        """
        if self.canvas is None:
            return
        
        try:
            if not self.canvas.winfo_exists():
                return
            
            import time
            current_time = time.time()
            time_since_last_update = current_time - self._last_update_time
            
            if time_since_last_update < 0.033:
                self._frame_skip_counter += 1
                if self._frame_skip_counter < 2:
                    return
                else:
                    self._frame_skip_counter = 0
            
            self._last_update_time = current_time
            
            resized_frame = cv2.resize(frame, (AppConfig.CAMERA_WIDTH, AppConfig.CAMERA_HEIGHT))
            
            img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
            imgtk = PIL.ImageTk.PhotoImage(image=img)
            
            old_image_id = self._image_id
            self._image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk
            
            if old_image_id is not None:
                self.canvas.delete(old_image_id) 
            
        except tk.TclError:
            return
        except Exception as e:
            pass
    
    def cleanup(self):
        """Clean up resources and clear canvas."""
        try:
            if self.canvas and self.canvas.winfo_exists():
                self.canvas.delete("all")
                if hasattr(self.canvas, 'image'):
                    delattr(self.canvas, 'image')
            self._image_id = None
        except:
            pass


class PreviewCameraManager:
    """Manages multiple preview camera feeds."""
    
    def __init__(self, parent):
        """
        Initialize the preview camera manager.
        
        Args:
            parent: Parent frame
        """
        self.parent = parent
        self.feeds = {}
        self.camera_container = None
        
    def setup(self):
        """Setup all preview camera feeds."""
        self.camera_container = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        self.camera_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.camera_container.grid_columnconfigure(0, weight=1)
        self.camera_container.grid_columnconfigure(1, weight=1)
        self.camera_container.grid_rowconfigure(0, weight=1)
        
        bf_feed = PreviewCameraFeed(self.camera_container, "BF Preview", "bf")
        bf_feed.create(row=0, column=0)
        self.feeds['bf'] = bf_feed
        
        od_feed = PreviewCameraFeed(self.camera_container, "OD Preview", "od")
        od_feed.create(row=0, column=1)
        self.feeds['od'] = od_feed
        
        return self.feeds
    
    def get_feed(self, feed_id):
        """
        Get a specific camera feed.
        
        Args:
            feed_id: Camera feed identifier ('od' or 'bf')
            
        Returns:
            PreviewCameraFeed instance or None
        """
        return self.feeds.get(feed_id)
