import shutil
import os

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