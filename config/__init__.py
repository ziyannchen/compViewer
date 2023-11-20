from utils.file import yaml_load

SSH_CONFIG = yaml_load('config/ssh.yaml')
WINDOW_CONFIG = yaml_load('config/window.yaml')

class WindowConfig:
    def __init__(self) -> None:
        for key, value in WINDOW_CONFIG.items():
            setattr(self, key, value)
    
windowConfig = WindowConfig()