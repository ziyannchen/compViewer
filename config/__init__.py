import os

from utils.file import yaml_load

class Config:
    def __init__(self, cfg_path) -> None:
        config = yaml_load(cfg_path)
        for key, value in config.items():
            setattr(self, key, value)

sshConfig = Config('config/ssh.yaml')
windowConfig = Config('config/window.yaml')

sshConfig.PrivateKeyPath = os.path.expanduser(sshConfig.PrivateKeyPath)
sshConfig.CacheDir = os.path.expanduser(sshConfig.CacheDir)