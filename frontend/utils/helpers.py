"""
Helper functions and utilities for the frontend.
"""

import tkinter as tk
from .styles import Colors, Fonts
from .debug_logger import debug_logger


def center_window(window, width=1280, height=800):
    """
    Center a window on the screen.
    
    Args:
        window: Tk window instance
        width: Window width
        height: Window height
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_header(parent, title, user_email, user_role, logout_callback, app_instance=None):
    """
    Create a header frame with logo and user info.
    
    Args:
        parent: Parent frame
        title: Application title
        user_email: Current user email
        user_role: Current user role
        logout_callback: Function to call on logout
        app_instance: Reference to main app instance (for debug toggle)
        
    Returns:
        Tuple of (header_frame, logout_button, debug_checkbutton)
    """
    header_frame = tk.Frame(parent, bg=Colors.PRIMARY_BG, height=85)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)
    
    logo_label = tk.Label(
        header_frame, 
        text=title, 
        font=Fonts.SUBTITLE,
        fg=Colors.WHITE, 
        bg=Colors.PRIMARY_BG
    )
    logo_label.pack(side=tk.LEFT, padx=20, pady=5)
    
    right_frame = tk.Frame(header_frame, bg=Colors.PRIMARY_BG)
    right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    
    user_label = tk.Label(
        right_frame, 
        text=f"{user_role}: {user_email}",
        font=Fonts.TEXT_BOLD, 
        fg=Colors.WHITE, 
        bg=Colors.PRIMARY_BG
    )
    user_label.pack(side=tk.LEFT, padx=(0, 10))
    
    button_container = tk.Frame(right_frame, bg=Colors.PRIMARY_BG)
    button_container.pack(side=tk.LEFT)
    
    logout_button = tk.Button(
        button_container, 
        text="Logout", 
        font=Fonts.SMALL_BOLD,
        bg=Colors.DANGER,
        fg=Colors.WHITE,
        relief=tk.RAISED,
        bd=2,
        padx=15,
        pady=3,
        cursor="hand2",
        command=logout_callback
    )
    logout_button.pack()
    
    debug_var = tk.BooleanVar(value=False)
    
    def on_debug_toggle():
        """Handle debug checkbox toggle."""
        if app_instance and hasattr(app_instance, 'current_tab_id'):
            page_name = app_instance.current_tab_id
            
            process_running = False
            process_name = ""
            
            if page_name == 'inference':
                if hasattr(app_instance, 'inspection_running') and app_instance.inspection_running:
                    process_running = True
                    process_name = "Inspection"
            elif page_name == 'settings':
                if hasattr(app_instance, 'tabs') and 'settings' in app_instance.tabs:
                    settings_tab = app_instance.tabs['settings']
                    if hasattr(settings_tab, 'preview_active') and settings_tab.preview_active:
                        process_running = True
                        process_name = "Preview"
            elif page_name == 'system_check':
                if hasattr(app_instance, 'system_check_running') and app_instance.system_check_running:
                    process_running = True
                    process_name = "System Check"
            
            if process_running:
                current_state = debug_logger.is_enabled(page_name)
                debug_var.set(current_state)
                
                from tkinter import messagebox
                messagebox.showwarning(
                    "Debug Mode Blocked",
                    f"⚠️ Cannot change debug mode while {process_name} is running!\n\n"
                    f"Please stop the {process_name} process first."
                )
                print(f"⚠️ Debug toggle blocked: {process_name} is running")
                return
            
            is_enabled = debug_logger.toggle_page(page_name)
            debug_var.set(is_enabled)
            
            if page_name == 'inference' and hasattr(app_instance, 'shared_data'):
                app_instance.shared_data["debug_enabled"] = is_enabled
            
            if is_enabled:
                debug_checkbutton.config(fg="#00ff00")
                print(f"✅ Debug mode ENABLED for {page_name}")
            else:
                debug_checkbutton.config(fg=Colors.WHITE)
                print(f"❌ Debug mode DISABLED for {page_name}")
    
    debug_checkbutton = tk.Checkbutton(
        button_container,
        text="Debug",
        variable=debug_var,
        font=Fonts.SMALL_BOLD,
        bg=Colors.PRIMARY_BG,
        fg=Colors.WHITE,
        selectcolor=Colors.SECONDARY_BG,
        activebackground=Colors.PRIMARY_BG,
        activeforeground=Colors.WHITE,
        cursor="hand2",
        command=on_debug_toggle,
        anchor="w",
        wraplength=150
    )
    debug_checkbutton.pack(pady=(1, 0), fill=tk.X)
    
    allow_images_checkbutton = None
    if app_instance:
        from .permissions import Permissions
        user_role = getattr(app_instance, 'current_role', 'Operator')
        can_access = Permissions.can_access_allow_all_images(user_role)
        
        if can_access:
            allow_images_var = tk.BooleanVar(value=False)
            
            def on_allow_images_toggle():
                """Handle allow images checkbox toggle."""
                if hasattr(app_instance, 'shared_data') and app_instance.shared_data is not None:
                    app_instance.shared_data['allow_all'] = allow_images_var.get()
                    status = "enabled" if allow_images_var.get() else "disabled"
                    print(f"Allow all images: {status}")
            
            allow_images_checkbutton = tk.Checkbutton(
                button_container,
                text="Allow all images",
                variable=allow_images_var,
                font=Fonts.SMALL_BOLD,
                bg=Colors.PRIMARY_BG,
                fg=Colors.WHITE,
                selectcolor=Colors.SECONDARY_BG,
                activebackground=Colors.PRIMARY_BG,
                activeforeground=Colors.WHITE,
                cursor="hand2",
                command=on_allow_images_toggle,
                anchor="w",
                wraplength=150
            )
            allow_images_checkbutton.pack(pady=(1, 0), fill=tk.X)
            
            app_instance.allow_images_var = allow_images_var
            app_instance.allow_images_checkbutton = allow_images_checkbutton
    
    if app_instance:
        if not hasattr(app_instance, 'debug_vars'):
            app_instance.debug_vars = {}
        app_instance.debug_checkbutton = debug_checkbutton
        app_instance.debug_var = debug_var
    
    return header_frame, logout_button, debug_checkbutton


def configure_notebook_style():
    """Configure ttk Notebook style for tabs."""
    import tkinter.ttk as ttk
    
    style = ttk.Style()
    style.theme_use('default')
    style.configure(
        'TNotebook.Tab', 
        background=Colors.PRIMARY_BG, 
        foreground=Colors.WHITE,
        font=('Arial', 12, 'bold'), 
        padding=[20, 10], 
        borderwidth=0
    )
    style.map(
        'TNotebook.Tab', 
        background=[('selected', Colors.SECONDARY_BG)],
        foreground=[('selected', Colors.WHITE)]
    )
    style.configure('TNotebook', background=Colors.PRIMARY_BG, borderwidth=0)
