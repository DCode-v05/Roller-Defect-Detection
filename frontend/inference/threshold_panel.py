"""
Threshold Panel Component
Displays and controls defect detection thresholds
"""

import tkinter as tk
import tkinter.ttk as ttk
from ..utils.styles import Colors, Fonts


class ThresholdPanel:
    """Panel for displaying and adjusting defect thresholds."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the threshold panel.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main app instance
        """
        self.parent = parent
        self.app = app_instance
        self.slider_values = {}
        
    def setup(self):
        """Setup the threshold panel UI."""
        threshold_panel = tk.LabelFrame(
            self.parent,
            text="Defect Threshold Controls",
            font=Fonts.LABEL_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=2
        )
        threshold_panel.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        od_frame = self._create_threshold_section(
            threshold_panel,
            "OD Defect Thresholds",
            self.app.od_defect_thresholds if self.app.od_defect_thresholds else {},
            row=0,
            column=0,
            is_od=True
        )
        
        bf_frame = self._create_threshold_section(
            threshold_panel,
            "BIG FACE Defect Thresholds",
            self.app.bf_defect_thresholds if self.app.bf_defect_thresholds else {},
            row=0,
            column=1,
            is_od=False
        )
        
        threshold_panel.grid_columnconfigure(0, weight=1)
        threshold_panel.grid_columnconfigure(1, weight=1)
        
        return threshold_panel
    
    def _create_threshold_section(self, parent, title, thresholds, row, column, is_od):
        """
        Create a threshold section for OD or Bigface.
        
        Args:
            parent: Parent frame
            title: Section title
            thresholds: Dictionary of defect thresholds
            row: Grid row position
            column: Grid column position
            is_od: Whether this is for OD camera
            
        Returns:
            Created frame
        """
        section_frame = tk.LabelFrame(
            parent,
            text=title,
            font=Fonts.TEXT_BOLD,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            bd=1
        )
        section_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        
        canvas = tk.Canvas(section_frame, bg=Colors.PRIMARY_BG, highlightthickness=0, height=200)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(section_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scroll_update_id = None
        
        def update_scroll_region(event=None):
            nonlocal scroll_update_id
            if scroll_update_id:
                canvas.after_cancel(scroll_update_id)
            scroll_update_id = canvas.after(100, lambda: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.bind('<Configure>', update_scroll_region)
        
        def on_mousewheel(event):
            canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        
        def bind_mousewheel(event=None):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_mousewheel(event=None):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        
        sliders_frame = tk.Frame(canvas, bg=Colors.PRIMARY_BG)
        canvas.create_window((0, 0), window=sliders_frame, anchor="nw")
        
        if thresholds:
            for idx, (defect, value) in enumerate(thresholds.items()):
                self._create_slider(sliders_frame, defect, value, idx, is_od)
        else:
            no_data_label = tk.Label(
                sliders_frame,
                text="No threshold data available",
                font=Fonts.TEXT,
                fg="#ffff00",
                bg=Colors.PRIMARY_BG,
                pady=20
            )
            no_data_label.pack()
        
        return section_frame
    
    def _create_slider(self, parent, defect_name, default_value, row, is_od):
        """
        Create a single threshold slider.
        
        Args:
            parent: Parent frame
            defect_name: Name of the defect
            default_value: Default threshold value
            row: Grid row position
            is_od: Whether this is for OD camera
        """
        frame = tk.Frame(parent, bg=Colors.PRIMARY_BG)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        
        label = tk.Label(
            frame,
            text=defect_name,
            font=Fonts.SMALL,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=20,
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=5)
        
        slider = ttk.Scale(
            frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=200
        )
        slider.set(default_value)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        value_label = tk.Label(
            frame,
            text=f"{default_value}%",
            font=Fonts.SMALL,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=5
        )
        value_label.pack(side=tk.RIGHT, padx=5)
        
        slider.configure(
            command=lambda val, lbl=value_label, defect=defect_name, is_od_val=is_od:
                self._update_threshold(val, lbl, defect, is_od_val)
        )
        
        key = f"{'od' if is_od else 'bf'}_{defect_name}"
        self.slider_values[key] = slider
    
    def _update_threshold(self, val, label, defect, is_od):
        """
        Update threshold value when slider moves.
        
        Args:
            val: New slider value
            label: Label widget to update
            defect: Defect name
            is_od: Whether this is for OD camera
        """
        label.config(text=f"{int(float(val))}%")
        
        if is_od:
            self.app.od_defect_thresholds[defect] = int(float(val))
        else:
            self.app.bf_defect_thresholds[defect] = int(float(val))
