"""
Window Configuration Module
Handles window startup configuration
"""


class WindowConfig:
    """Window configuration for maximized and focused startup."""
    
    @staticmethod
    def configure(window):
        """
        Configure the window for optimal display.
        
        Args:
            window: Tk window instance to configure
        """
        window.lift()
        window.focus_force()
        
        window.state('zoomed')
