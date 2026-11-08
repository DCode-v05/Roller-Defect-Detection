"""
Navigation Bar Configuration
Defines the navigation structure and button configurations
"""


class NavConfig:
    """Navigation bar configuration constants."""
    
    NAV_BUTTONS = [
        ("inference", "INFERENCE", "Inference"),
        ("data", "DATA", "Data"),
        ("diagnosis", "DIAGNOSIS", "Diagnosis"),
        ("settings", "SETTINGS", "Settings"),
        ("model_management", "MODEL MANAGEMENT", "Model Management"),
        ("user_management", "USER MANAGEMENT", "User Management"),
        ("system_check", "SYSTEM CHECK", "System Check"),
        ("backup", "BACKUP", "Backup"),
        ("info", "INFO", "Info"),
    ]
    
    NAVBAR_HEIGHT = 50
    BUTTON_GAP = 3
    NAVBAR_PADDING_X = 5
    NAVBAR_PADDING_Y = 3
    
    @classmethod
    def get_button_configs(cls):
        """Get all button configurations as a list of tuples."""
        return cls.NAV_BUTTONS
    
    @classmethod
    def get_button_ids(cls):
        """Get list of all button IDs."""
        return [btn[0] for btn in cls.NAV_BUTTONS]
    
    @classmethod
    def get_button_text(cls, button_id):
        """Get button text for a given button ID."""
        for btn_id, text, _ in cls.NAV_BUTTONS:
            if btn_id == button_id:
                return text
        return None
    
    @classmethod
    def get_tab_name(cls, button_id):
        """Get tab name for a given button ID."""
        for btn_id, _, tab_name in cls.NAV_BUTTONS:
            if btn_id == button_id:
                return tab_name
        return None
