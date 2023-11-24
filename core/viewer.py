import os
import math
from copy import deepcopy
from PyQt5.QtWidgets import (QMainWindow, QDialog, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import QPoint

from ui import MainWindowUI
from utils.file import fuzzySearchList
from utils.check import checkOverflow
from config import sshConfig, windowConfig
from .dialogs import Dialog
from .media import requestQMedia
from .files import fileHandler
from .remote import SSHConnection
from .events import EventHandler

class ViewerApp(QMainWindow, MainWindowUI):
    def __init__(self):
        super(ViewerApp, self).__init__()
        # for debug
        import cProfile
        self.profiler = cProfile.Profile()

        # files
        self.file_handler = None
        self.ssh_client = None
        # defind func to fit remote or local features
        self.initApp()

        # UI window
        self.setWindow(self)
        self.lastMousePos = QPoint()
        self.setupUi(self)
        self.bindEvent()

    def initApp(self, keep_ssh=False):
        if not keep_ssh and self.ssh_client is not None:
            del self.ssh_client # # call __del__ func of ssh_client
            self.ssh_client = None
        if self.file_handler is not None:
            del self.file_handler # call __del__ func of fileHandler

        self.setCentralWidget(None) # clear the whole window
        self.file_handler = fileHandler(self)

        self.windowCfg = deepcopy(windowConfig)
        self.view_adjusted = False
        self.mousePressed = False

    @property
    def imageFilenames(self):
        return self.file_handler.imageFilenames
    
    @property
    def folderPaths(self):
        return self.file_handler.folderPaths
    
    @property
    def graphicsViews(self):
        return self.file_handler.graphicsViews
    
    @property
    def currentIndex(self):
        return self.file_handler.currentIndex
    
    @currentIndex.setter
    def currentIndex(self, value):
        '''currentIndex.setter func
        When self.currentIndex is set (arbitrary 'self.currentIndex=' clause), 
            this func will be called automatically with param value as the set value.
        This feature is based on self.currentIndex is decorated as a property key.
        '''
        setattr(self.file_handler, 'currentIndex', value)
        max_image_idx = len(self.imageFilenames) - 1
        if self.currentIndex < 0:
            QMessageBox.information(self, 'Info', 'You\'re in the beginning of the directory! Skip to the tail...')
            setattr(self.file_handler, 'currentIndex', max_image_idx)
        elif self.currentIndex > max_image_idx:
            QMessageBox.information(self, 'Info', 'You\'re in the end of the directory! Skip to the start...')
            setattr(self.file_handler, 'currentIndex', 0)
    
    @property
    def titles(self):
        return self.file_handler.titles

    def bindEvent(self):
        # file
        self.actionLoadSubFolders.triggered.connect(self.loadAllSubFolders)
        # need to use key lambda when call func from prop even though no param passed
        self.actionAdd1Folder.triggered.connect(lambda: self.file_handler.addFolder())
        # TODO: del assigned dir
        self.actionDel1Folder.triggered.connect(lambda: self.file_handler.deleteFolder())
        self.actionSave.triggered.connect(lambda: self.file_handler.saveView())
        # self.actionSave.triggered.connect(self.save)
        # TODO: log in assigned host
        self.actionOpenRemote.triggered.connect(lambda: self.connectRemote('test_host1'))

        self.actionGoTo.triggered.connect(self.actionGoToTriggered)
        self.actionGoToName.triggered.connect(lambda: self.actionGoToTriggered(by_name=True))

    def update(self):
        def get_dir(filename):
            loc = '' # define media file is in local or remote
            if ':' in filename:  loc, filename = filename.split(':')
            if loc == 'cache':
                cached_dir = os.path.join(sshConfig.CacheDir, relative_fdir)
                print(f'Reading', filename, f'from cached folder {cached_dir}')
                return cached_dir, loc
            return self.folderPaths[key], loc
        
        # self.profiler.enable()
        filename = self.imageFilenames[self.currentIndex]
        for idx, (key, view) in enumerate(self.graphicsViews.items()):
            relative_fdir = os.path.join(self.folderPaths[key].split(os.sep)[-2], key)
            folder, loc = get_dir(filename)
            file_path = os.path.join(folder, filename)
            # add media obj
            file_bytes = None
            if self.ssh_client is not None and loc != 'cache':
                # media file can only be access from remote, read remote file bytes
                # remote bytes will be cached to the local dir automatically when request qMedia from bytes
                # TODO: currently cache video only
                file_bytes = self.ssh_client.get_remote_file_content(file_path) # file bytes
                # replace with local sign to avoid repeated remote access
                file_path = os.path.join(sshConfig.CacheDir, relative_fdir, filename)
                self.imageFilenames[self.currentIndex] = 'cache:' + filename

            qMedia = requestQMedia(file_path, file_bytes=file_bytes, fdir=relative_fdir)
            qText = qMedia.get_title(self, file_path)
            if not self.view_adjusted: self.adjustGraphicsView(idx, qMedia.width, qMedia.height)
            view.scene().clear() # scene clearing after qText created, avoid qText to be cleared
            try:
                view.scene().addPixmap(qMedia.item)
            except:
                view.scene().addItem(qMedia.item) # video
            view.scene().addItem(qText)
            view.show()

        self.view_adjusted = True
        # self.profiler.disable()
        # self.profiler.print_stats()

    def adjustGraphicsView(self, idx, media_w, media_h):
        '''Adjust QGraphicsView geometry in the main window to build media view grids.
        Args:
            idx: specify the index of the graphicsViews list. 
                used to 1) calculate the position of the view in the main window, and 2) set view geometry.
            media_w: media width in the scene.
            media_h: media height in the scene.
        '''
        border = self.windowCfg.BORDER
        x_margin, y_margin = self.windowCfg.MARGIN_W, self.windowCfg.MARGIN_H
        screen_w, screen_h = self.size().width(), self.size().height() # app window size
        vsize_w, vsize_h = media_w, media_h # view size, default to media size
        # 获取主屏幕长宽
        # screen = QDesktopWidget().screenGeometry()
        # screen_w, screen_h = screen.width(), screen.height()
        x_num = self.windowCfg.X_NUM
        media_num = len(self.folderPaths.keys())
        if x_num == 'auto':
            # 预设的media面积远大于屏幕面积，需要调整view的缩放比例
            v_scale = max(1, media_num*media_h*media_w // (screen_w*screen_h) - 1)
            vsize_w /= v_scale; vsize_h /= v_scale
            self.windowCfg.X_NUM = x_num = max(1, (screen_w - 2 * x_margin) // (vsize_w + border))
        y_num = math.ceil(media_num / x_num)

        # readjust unsuitable view size to fit the app screen window
        if x_num * vsize_w + border > screen_w:
            vsize_w = (screen_w - 2 * x_margin - border * (x_num - 1)) // x_num
            vsize_h = (media_h / media_w) * vsize_w # keep the aspect ratio
        if y_num * vsize_h + border > screen_h:
            vsize_h = (screen_h - 2 * y_margin - border * (y_num - 1)) // y_num
            vsize_w = (media_w / media_h) * vsize_h # keep the aspect ratio
        # print(vsize_w, vsize_h)
        
        x_crt = idx % (x_num)
        y_crt = idx // (x_num)
        x = x_margin + x_crt * (vsize_w + border)
        y = y_margin + y_crt * (vsize_h + border)
        list(self.graphicsViews.values())[idx].setGeometry(x, y, vsize_w, vsize_h)
        # print('view pos', x, y, vsize_w, vsize_h)

    def loadAllSubFolders(self):
        self.initApp() # init app window
        self.file_handler.loadAllSubFolders()
    
    def connectRemote(self, cfg_name):
        cfg = getattr(sshConfig, cfg_name)
        self.ssh_client = SSHConnection(
            host = cfg['HostName'],
            user = cfg['User'],
            port = cfg['Port'],
            private_key_path=sshConfig.PrivateKeyPath)
        # print(self.ssh_client)
        dialog = Dialog(title=f'Remote '+cfg['HostName'], label='paths(split by ;)', edit='text')
        result = dialog.exec_()
        if result == QDialog.Accepted:
            input_text = dialog.get_input_text()
            input_text = path_list = '/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/experiments/train_GFPGANv3_video_v1_sliding_window/visualization_mp4/50000;/cpfs01/user/chenziyan/BFRxBenchmark/tmp/GFPGAN/results/gfpgan_unaligned/vfhq/interval1_LR_Blind_mp4/restored_faces'
            path_list = input_text.split(';')
            self.initApp(keep_ssh=True) # init app window
            self.file_handler.loadFromRemote(path_list, self.ssh_client)

    def keyPressEvent(self, event):
        EventHandler.keyPressedEvent(self, event)

    def wheelEvent(self, event):
        for key in self.graphicsViews.keys():
            view = self.graphicsViews[key]
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
            view.scale(factor, factor)
            title_item = self.titles[key]
            # 获取视图的左上角在场景中的坐标
            targetPos = view.mapToScene(0, 0)  # 视图左上角的场景坐标
            title_item.setPos(targetPos)  # 吸附到目标位置
            title_item.setScale(title_item.scale() * (1 / factor))

    def mousePressEvent(self, event):
        self.mousePressed = True
        self.lastMousePos = event.pos()

    def mouseReleaseEvent(self, event):
        self.mousePressed = False

    def mouseMoveEvent(self, event) -> None:
        if self.mousePressed:
            # 计算鼠标移动距离
            dx = event.x() - self.lastMousePos.x()
            dy = event.y() - self.lastMousePos.y()
            self.lastMousePos = event.pos()

            # 更新图片位置 and titles
            for key in self.graphicsViews.keys():
                view = self.graphicsViews[key]
                h, v = view.horizontalScrollBar().value(), view.verticalScrollBar().value()
                if not checkOverflow(h - dx, 'int32') or not checkOverflow(v - dy, 'int32'):
                    print(f'Int32 overflow... could not scale to {h - dx}, {v - dy}')
                    return
                view.horizontalScrollBar().setValue(h - dx)
                view.verticalScrollBar().setValue(v - dy)
                title_item = self.titles[key]
                # 获取视图的左上角在场景中的坐标
                targetPos = view.mapToScene(0, 0)  # 视图左上角的场景坐标
                title_item.setPos(targetPos)  # 吸附到目标位置
    
    def resizeEvent(self, event):
        # 调用基类的 resizeEvent 方法
        super(ViewerApp, self).resizeEvent(event)
        windowConfig.WINDOW_SIZE_W = 'auto'
        # readjust view grid when the app window resized
        self.view_adjusted = False

    def actionGoToTriggered(self, by_name=False):
        label = 'Name' if by_name else 'Index'
        dialog = Dialog(title='GoTo', label=label)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            input_text = dialog.get_input_text()
            # print("Input Text:", input_text)
            if label == 'Name':
                index = fuzzySearchList(input_text, self.imageFilenames)
                if index == -1:
                    QMessageBox.critical(self, "Name Not found", f'No filename includes \'{input_text}\'!')
                    return
            else:
                index = int(input_text)
                #TODO: check int
                if index > len(self.imageFilenames) - 1 or index < 0:
                    QMessageBox.critical(f'Invalid Index {index}!')
                    return 
            self.currentIndex = index
            self.update()
        
        