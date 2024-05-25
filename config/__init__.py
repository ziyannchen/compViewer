import os
import ast
from utils.file import yaml_load

class Config:
    def __init__(self, cfg_path) -> None:
        config = yaml_load(cfg_path)
        for key, value in config.items():
            setattr(self, key, value)
        self.onChanged()

    def set(self, obj):
        for attr, value in obj.items():
            if not isinstance(getattr(self, attr), str):
                value = ast.literal_eval(value)
            setattr(self, attr, value)
        self.onChanged()
    
    def onChanged(self):
        pass

class WindowConfig(Config):
    def onChanged(self):
        self.CACHE_DIR = os.path.expanduser(self.CACHE_DIR)
        for key, value in self.SUPPORTED_FILES.items():
            self.SUPPORTED_FILES[key] = tuple(value)

windowConfig = WindowConfig('config/window.yaml')