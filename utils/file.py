import shutil
import os
import yaml
from collections import OrderedDict

def copyFile(dst, src, verbose=True):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(src):
        if verbose:
            print(f'File {src} does not exist')
        return False
    
    return shutil.copyfile(src, dst)

def fuzzySearch(pattern, string):
    pattern = pattern.lower()
    string = string.lower()
    return pattern in string

def fuzzySearchList(pattern, list):
    for index, item in enumerate(list):
        if fuzzySearch(pattern, item):
            return index
    return -1

def scanDir(folder, recursive=False, full_path=False, suffix=('.png', '.jpg', '.jpeg')):
        '''
        Args:
            recursive: to load images in folder and subfolders recursively. (TODO)
        '''
        if not recursive:
            filenames = [f for f in os.listdir(folder) if f.endswith(suffix)]
        if full_path:
            filenames = [os.path.join(folder, f) for f in filenames]
        filenames.sort()

        return filenames

def yaml_load(f):
    """Load yaml file or string.

    Args:
        f (str): File path or a python string.

    Returns:
        dict: Loaded dict.
    """
    if os.path.isfile(f):
        with open(f, 'r') as f:
            return yaml.safe_load(f)
    else:
        return yaml.safe_load(f)