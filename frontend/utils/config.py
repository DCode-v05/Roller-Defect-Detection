"""
Application Configuration
"""


class AppConfig:
    """Application configuration constants."""
    
    WINDOW_WIDTH = 1366
    WINDOW_HEIGHT = 768
    WINDOW_TITLE = "WELVISION"
    
    CAMERA_WIDTH = 580
    CAMERA_HEIGHT = 380
    
    PLC_IP = "172.17.8.17"
    PLC_RACK = 0
    PLC_SLOT = 1
    PLC_DB_NUMBER = 86
    
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "root"
    DB_DATABASE = "welvision_db"
    
    CAMERA_FRAME_WIDTH = 1280
    CAMERA_FRAME_HEIGHT = 960
    
    WARMUP_BF = r"Warmup BF.jpg"
    WARMUP_OD = r"Warmup OD.jpg"
