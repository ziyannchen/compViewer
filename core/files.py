import os
from natsort import natsorted


from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from utils.file import copy_file, scan_dir
from config import windowConfig
from core.view import captureView
# from core.remote import REMOTE_SIGN

SUPPORTED_FILES = sum(windowConfig.SUPPORTED_FILES.values(), ())

class fileHandler:
    def __init__(self, main_window) -> None:
        self.main_window = main_window
        self.initAll()
        
    def initAll(self):
        self.folderPaths = {}

        self.imageFilenames = None
        self.titles = {}

    @property
    def ssh_client(self):
        return self.main_window.ssh_client
    
    def set_imageFilenames(self, value):
        if self.imageFilenames is None:
            self.imageFilenames = value
        else:
            self.imageFilenames = list(set((*value, *self.imageFilenames)))
        self.imageFilenames = natsorted(self.imageFilenames)
        # print(f'Total {len(self.imageFilenames)} files counted')

    def checkFolder(self, verbose=False):
        for filename in self.imageFilenames:
            for k, folder in self.folderPaths.items():
                if not os.path.exists(os.path.join(folder, filename)):
                    if verbose:
                        print(f'File {filename} does not exist in folder {folder}')
                    continue
            self.imageFilenames.remove(filename)
                    
    def deleteFolder(self):
        '''
        Delete the last one folder by default.
        TODO: delete the selected folder.
        '''
        if len(self.folderPaths) == 0:
            print('No folder loaded')
            return None
        base_key = list(self.folderPaths.keys())[-1]
        del self.folderPaths[base_key]
        self.checkFolder()
        return base_key

    def loadFolder(self, folder, check_dir=os.path.isdir, scan_func=scan_dir):
        # TODO: 暂不支持文件夹嵌套

        # def check_key(base_key, folder):
        #     if base_key in self.folderPaths.keys():
        #         pfolder = os.path.dirname(folder)
        #         base_key = os.path.join(os.path.basename(pfolder), base_key)
        #         return check_key(base_key, pfolder)
        #     return base_key
        print('loadFolder', folder, os.path.isdir(folder))
        tmp_files = []
        base_key = None
        if check_dir(folder):
            base_key = os.path.basename(folder)
            # base_key = check_key(base_key, folder)
            print('loadFolder', base_key, self.folderPaths.keys(), folder, base_key in self.folderPaths.keys())
            if base_key in self.folderPaths.keys():
                print(f'Folder {folder} already loaded')
                return -1, base_key
            self.folderPaths[base_key] = folder
            # self.createGraphicsView(base_key)
            
            tmp_files = scan_func(folder=self.folderPaths[base_key], suffix=SUPPORTED_FILES, full_path=False)

            print(f'Indexing from base key ', base_key)
            print(f'Folder {folder} loaded, {len(tmp_files)} files found')

        self.set_imageFilenames(tmp_files)
        return len(tmp_files), base_key

    def addFolder(self, folder=None, **kargs):
        if folder is None:
            all_folders = list(self.folderPaths.values())
            default_path = all_folders[-1] if len(all_folders) else os.path.expanduser('~')
            folder = QFileDialog.getExistingDirectory(self.main_window, "Select Folder", default_path)
        
        return self.loadFolder(folder, **kargs)

    def getAllSubFolders(self, target=None):
        if target is None:
            target = QFileDialog.getExistingDirectory(self.main_window, "Select Folder")
            if not target:
                return []
        target = QDir.toNativeSeparators(target)
        dirs = natsorted(os.listdir(target))
        print(dirs)
        return [os.path.join(target, d) for d in dirs if not d.startswith('.')]
    
    # def loadFromRemote(self, path_list, ssh_client):
    #     for path in path_list:
    #         # print(self.ssh_connector.getAllFiles(path))
    #         self.loadFolder(path, check_dir=any, # path not need to be checked for files are from ls clause
    #             scan_func=ssh_client.getAllFiles)
    #     self.main_window.update()
    
    def saveImageGroup(self, graphicsViews, index, save_dir, scale_view=False):
        imgname, ext = os.path.splitext(self.imageFilenames[index])
        save_dir = os.path.join(save_dir, f'{index}_{imgname}')
        os.makedirs(save_dir, exist_ok=True)
        
        message_info = ['Info', f'Saved susccessfully to {save_dir}']
        for key, view in graphicsViews.items():
            source_folder = self.folderPaths[key]
            if self.ssh_client is not None and not os.path.exists(source_folder):
                source_folder = os.path.join(windowConfig.CACHE_DIR, self.get_relative_fdir(key))
            
            img_path = os.path.join(source_folder, imgname+ext)
            target_path = os.path.join(save_dir, f'{key}{ext}')
            if scale_view:
                captureView(view, img_path, target_path, remove_item=self.titles[key])
                print('Saved crops in ', target_path)
            else:
                if not copy_file(target_path, img_path):
                    print(f'Copy {img_path} failed')
                    message_info[0] = 'Error'
                    message_info[1] = f'Copy {img_path} failed\n'
                    QMessageBox.critical(self.main_window, *message_info)
                    return 
        QMessageBox.information(self.main_window, *message_info)

    def get_relative_fdir(self, key):
        paths = self.folderPaths[key].split(os.sep)
        return os.path.join(paths[-3], paths[-2], key)

    def loadFileBytes(self, key):
        '''
        load file from local directory or remote.
            if load from remote, cache in local temp file for fast access.
        '''
        filename = self.imageFilenames[self.main_window.currentIndex]
        relative_fdir = self.get_relative_fdir(key)
        
        fpath = os.path.join(self.folderPaths[key], filename)
        print(fpath)
        if os.path.exists(fpath):
            print('Reading from local file ', fpath)
            file_bytes = read_bytes(fpath)
        elif self.ssh_client is not None:
            # read remote media file bytes, and cache to local dirs automatically
            # TODO: currently cache video only.
            # TODO: support HASH to update local file
            # FIXME: media file cleared for unknown reason
            fdir_local = os.path.join(windowConfig.CACHE_DIR, relative_fdir)
            fpath_local = os.path.join(fdir_local, filename)
            if not os.path.exists(fpath_local):
                try:
                    print('Reading from remote path', fpath)
                    file_bytes = self.ssh_client.get_remote_file_content(fpath) # file bytes
                    cache_bytes(fpath_local, file_bytes)
                except Exception as e:
                    print(e)
                    QMessageBox.critical(self.main_window, "Remote Error ", f'{e}!')
                    return None, None
            else:
                file_bytes = read_bytes(fpath)
            # replace with local sign to avoid repeated remote access
            fpath = fpath_local
            # self.folderPaths[key] = fdir_local
        else:
            raise FileNotFoundError(f'File {fpath} does not exist')
            
        return fpath, file_bytes

def cache_bytes(path, file_bytes, verbose=True):
    '''Save media bytes to local path.'''
    save_dir = os.path.dirname(path)
    os.makedirs(save_dir, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(file_bytes)
    if verbose:
        print('Caching file bytes to', path)

def read_bytes(path, verbose=True):
    '''Load media bytes from local path.'''
    if not os.path.exists(path):
        if verbose:
            print(f'File {path} does not exist')
        return None
    if verbose:
        print('Loading file bytes from', path)
    with open(path, 'rb') as f:
        return f.read()