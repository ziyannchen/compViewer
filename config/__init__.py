import os
import ast
from utils.file import yaml_load

class Config:
    def __init__(self, cfg_path) -> None:
        config = yaml_load(cfg_path)
        for key, value in config.items():
            setattr(self, key, value)

    def set(self, obj):
        for attr, value in obj.items():
            if not isinstance(getattr(self, attr), str):
                value = ast.literal_eval(value)
            setattr(self, attr, value)

windowConfig = Config('config/window.yaml')
windowConfig.CACHE_DIR = os.path.expanduser(windowConfig.CACHE_DIR)

for key, value in windowConfig.SUPPORTED_FILES.items():
    windowConfig.SUPPORTED_FILES[key] = tuple(value)