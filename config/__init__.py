import os

from utils.file import yaml_load

class Config:
    def __init__(self, cfg_path) -> None:
        config = yaml_load(cfg_path)
        for key, value in config.items():
            setattr(self, key, value)

windowConfig = Config('config/window.yaml')
windowConfig.CACHE_DIR = os.path.expanduser(windowConfig.CACHE_DIR)

for key, value in windowConfig.SUPPORTED_FILES.items():
    windowConfig.SUPPORTED_FILES[key] = tuple(value)