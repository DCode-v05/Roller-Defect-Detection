"""
GUI Application Title Management Component
Allows SuperAdmin to change the application title
"""

import tkinter as tk
from tkinter import messagebox
from ..utils.styles import Colors, Fonts
from ..utils.permissions import Permissions
from .info_database import InfoDatabase


class TitleManagement:
    """Component for managing GUI application title."""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the title management component.
        
        Args:
            parent: Parent frame
            app_instance: Reference to main WelVisionApp instance
        """
        self.parent = parent
        self.app = app_instance
        self.db = InfoDatabase()
        
        self.title_entry = None
        self.current_title_label = None
    
    def create(self):
        """Create the title management UI."""
        user_role = getattr(self.app, 'current_role', 'Operator')
        
        can_change_title = Permissions.can_change_gui_title(user_role)
        
        if not can_change_title:
            return
        
        main_frame = tk.LabelFrame(
            self.parent,
            text="🔧 GUI Application Title Management (Super Admin Only)",
            font=Fonts.HEADER,
            fg="#FFA500",
            bg=Colors.PRIMARY_BG,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.pack(fill=tk.X, padx=10, pady=10)
        
        container = tk.Frame(main_frame, bg=Colors.PRIMARY_BG)
        container.pack(fill=tk.X, padx=20, pady=15)
        
        section_title = tk.Label(
            container,
            text="📝 Change Application Title",
            font=Fonts.TEXT_BOLD,
            fg="#FFD700",
            bg=Colors.PRIMARY_BG
        )
        section_title.pack(anchor=tk.W, pady=(0, 10))
        
        current_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        current_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            current_frame,
            text="Current GUI Title:",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5)
        
        current_title = self.db.get_app_title()
        
        self.current_title_label = tk.Label(
            current_frame,
            text=f'"{current_title}"',
            font=Fonts.TEXT_BOLD,
            fg="#FFD700",
            bg=Colors.PRIMARY_BG,
            anchor=tk.W
        )
        self.current_title_label.pack(side=tk.LEFT, padx=5)
        
        entry_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        entry_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            entry_frame,
            text="New GUI Title:",
            font=Fonts.TEXT,
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG,
            width=20,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5)
        
        self.title_entry = tk.Entry(
            entry_frame,
            font=Fonts.TEXT,
            bg=Colors.WHITE,
            fg=Colors.PRIMARY_BG,
            width=50
        )
        self.title_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.title_entry.insert(0, current_title)
        
        buttons_frame = tk.Frame(container, bg=Colors.PRIMARY_BG)
        buttons_frame.pack(pady=15)
        
        tk.Button(
            buttons_frame,
            text="Update Title",
            font=Fonts.TEXT_BOLD,
            bg="#007BFF",
            fg=Colors.WHITE,
            activebackground="#0056b3",
            activeforeground=Colors.WHITE,
            command=self.update_title,
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="Reset to Default",
            font=Fonts.TEXT_BOLD,
            bg="#6C757D",
            fg=Colors.WHITE,
            activebackground="#545b62",
            activeforeground=Colors.WHITE,
            command=self.reset_to_default,
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="Preview",
            font=Fonts.TEXT_BOLD,
            bg="#17A2B8",
            fg=Colors.WHITE,
            activebackground="#117a8b",
            activeforeground=Colors.WHITE,
            command=self.preview_title,
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        note_label = tk.Label(
            container,
            text="⚠️ Note: Title changes will be applied immediately and saved to the system configuration.",
            font=Fonts.SMALL,
            fg="#FFA500",
            bg=Colors.PRIMARY_BG,
            wraplength=700,
            justify=tk.LEFT
        )
        note_label.pack(anchor=tk.W, pady=(10, 0))
    
    def update_title(self):
        """Update the application title."""
        new_title = self.title_entry.get().strip()
        
        if not new_title:
            messagebox.showerror("Error", "Title cannot be empty!")
            return
        
        current_title = self.db.get_app_title()
        if new_title == current_title:
            messagebox.showinfo("No Change", "The new title is the same as the current title.")
            return
        
        if self.db.update_app_title(new_title, self.app.current_user):
            self.app.title(new_title)
            
            self.current_title_label.config(text=f'"{new_title}"')
            
            messagebox.showinfo(
                "Success",
                f"Application title updated to:\n\n'{new_title}'\n\n"
                "The change has been saved to the system configuration."
            )
        else:
            messagebox.showerror("Error", "Failed to update application title!")
    
    def reset_to_default(self):
        """Reset title to default."""
        default_title = "WELVISION"
        
        response = messagebox.askyesno(
            "Confirm Reset",
            f"Are you sure you want to reset the title to:\n\n'{default_title}'?"
        )
        
        if response:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, default_title)
            self.update_title()
    
    def preview_title(self):
        """Preview the title without saving."""
        new_title = self.title_entry.get().strip()
        
        if not new_title:
            messagebox.showerror("Error", "Title cannot be empty!")
            return
        
        original_title = self.app.title()
        self.app.title(new_title)
        
        response = messagebox.askyesno(
            "Title Preview",
            f"Preview: '{new_title}'\n\n"
            "Do you want to save this title?"
        )
        
        if response:
            self.update_title()
        else:
            self.app.title(original_title)
    
    def refresh_current_title(self):
        """Refresh the current title display."""
        current_title = self.db.get_app_title()
        self.current_title_label.config(text=f'"{current_title}"')
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, current_title)
