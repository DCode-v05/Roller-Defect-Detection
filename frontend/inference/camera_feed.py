"""
Camera Feed Component
Displays live camera feeds with annotations
"""

import tkinter as tk
import cv2
import PIL.Image
import PIL.ImageTk
import numpy as np
import time
from ..utils.styles import Colors, Fonts
from ..utils.config import AppConfig


class CameraFeed:
    """Component for displaying a single camera feed."""
    
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
        camera_frame = tk.LabelFrame(
            self.parent,
            text=self.title,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=0,
            highlightthickness=0
        )
        camera_frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
        
        self.canvas = tk.Canvas(
            camera_frame,
            bg=Colors.BLACK,
            width=AppConfig.CAMERA_WIDTH,
            height=AppConfig.CAMERA_HEIGHT,
            highlightthickness=0
        )
        self.canvas.pack(padx=5, pady=5)
        
        return camera_frame
    
    def update_frame(self, frame):
        """
        Update the displayed frame.
        
        Args:
            frame: OpenCV frame (BGR format)
        """
        if self.canvas is None:
            return
        
        try:
            if not self.canvas.winfo_exists():
                return
            
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
            print(f"Error updating camera feed: {e}")
            return
    
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


class CameraFeedManager:
    """Manages multiple camera feeds."""
    
    def __init__(self, parent):
        """
        Initialize the camera feed manager.
        
        Args:
            parent: Parent frame
        """
        self.parent = parent
        self.feeds = {}
        self.camera_frame = None
        
    def setup(self, parent=None):
        """Setup all camera feeds."""
        target_parent = parent if parent else self.parent
        
        self.camera_frame = tk.Frame(target_parent, bg=Colors.PRIMARY_BG)
        self.camera_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.camera_frame.grid_columnconfigure(0, weight=1)
        self.camera_frame.grid_columnconfigure(1, weight=1)
        self.camera_frame.grid_rowconfigure(0, weight=1)
        
        bf_feed = CameraFeed(self.camera_frame, "BF Feed", "bf")
        bf_feed.create(row=0, column=0)
        self.feeds['bf'] = bf_feed
        
        od_feed = CameraFeed(self.camera_frame, "OD Feed", "od")
        od_feed.create(row=0, column=1)
        self.feeds['od'] = od_feed
        
        return self.feeds
    
    def get_feed(self, feed_id):
        """
        Get a specific camera feed.
        
        Args:
            feed_id: Camera feed identifier ('od' or 'bf')
            
        Returns:
            CameraFeed instance or None
        """
        return self.feeds.get(feed_id)
