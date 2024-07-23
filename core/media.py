import os
import cv2

from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt, QSizeF, QRect, QFileInfo
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsPixmapItem, QGraphicsProxyWidget, QLabel, QWidget, QVBoxLayout
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from config import windowConfig

class AbstractMedia:
    def __init__(self, path, bytes=None, view=None):
        self.path = path
        self.bytes = bytes
        self.width = None 
        self.height = None
        self.item = None
        self.view = view

    def _load(self):
        # implement 1) load mead from path or file bytes; 2) do proper resize and add to view.scene()
        raise NotImplementedError

    def load_media(self):
        self.view.scene().clear() # scene clearing after qText created, avoid qText to be cleared
        self._load()

    def force_resize(self):
        self.set_size(windowConfig.MEDIA_W, windowConfig.MEDIA_H)
    
    def set_size(self, w, h):
        self.width, self.height = w, h
    
    def __del__(self):
        del self.item

def load_gif_obj(path) -> QtGui.QMovie:
    '''Load QMovie object from local gif file path.
    Args:
        path: str, local gif file path.
    '''
    assert path.endswith('.gif'), f'Only support .gif file, but got {path}'
    assert os.path.exists(path), f'File {path} does not exist.'
    movie = QtGui.QMovie(path)
    return movie

def load_image_obj(path=None, bytes=None, scale=True) -> QtGui.QPixmap:
    '''Load Qpixmap from local image file path or file bytes.
    Args:
        path: str, load pixel map from a local image file path.
        bytes: bytes, load pixel map from image bytes.
        scale: bool, whether to scale the image according to config file. Default: True
    '''
    assert bytes or path, 'Either bytes or path should be provided.'
    if bytes:
        # file bytes
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(bytes)
    else:
        pixmap = QtGui.QPixmap(path)
    if scale:
        pixmap.scaledToWidth(windowConfig.IMG_SIZE_W)
    return pixmap

class QVideoObj(AbstractMedia):
    def _load(self):
        self.size_set = False
        self.force_resize()

        self.item = QGraphicsVideoItem()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.view.scene().addItem(self.item)
        self.media_player.setVideoOutput(self.item)

        if QFileInfo(self.path).exists():
            # 设置 QGraphicsVideoItem 显示的内容
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.path)))
            
            self.media_player.stateChanged.connect(self.video_state_changed)
            self.media_player.error.connect(self.media_error)
            self.media_player.play()
            
            # 异步函数，需要等待视频加载完成. 容易bug的地方：主函数先执行，后执行视频媒体读取
            self.item.nativeSizeChanged.connect(self.resize_view)
            # print('video media playing...')
            # print('native size in _load', self.item.nativeSize())

    def resize_view(self):
        # ensure that the view is always below any other child
        self.view.lower()
        # make the view as big as the parent
        
        if not self.size_set:
            size = self.item.nativeSize()
            self.set_size(size.width(), size.height())
            self.size_set = True

        # resize the item to the video size
        size = QSizeF(self.width, self.height)
        self.view.resize(self.width, self.height)
        self.item.setSize(size)

        # fit the whole viewable area to the item and crop exceeding margins
        # self.view.fitInView(
        #     self.item, Qt.KeepAspectRatioByExpanding)

        # scroll the view to the center of the item
        # self.view.centerOn(self.item)
        
    def media_error(self, error):
        print(f"Error: {self.media_player.errorString()}")
    
    def video_state_changed(self, state):
        if state == QMediaPlayer.StoppedState:
            '''Set infinite loop playback for video.'''
            # Restart the video when it reaches the end
            # self.media_player.setPosition(0)
            self.media_player.play()
        elif state == QMediaPlayer.PlayingState:
            # print("Media is playing...")
            pass
        elif state == QMediaPlayer.PausedState:
            # print("Media is paused...")
            pass

class QGifObj(AbstractMedia):
    def _load(self):
        gif_obj = load_gif_obj(self.path)

        label = QLabel()
        label.setMovie(gif_obj)

        self.item = QGraphicsProxyWidget()
        self.item.setWidget(label)
        label.show()

        self.view.scene().addItem(self.item)
        gif_obj.start()
        frame_size = gif_obj.currentImage()
        # print('GIF size', frame_size.width(), frame_size.height())
        self.set_size(frame_size.width(), frame_size.height())

class QImageObj(AbstractMedia):
    def _load(self):
        assert self.path.endswith(windowConfig.SUPPORTED_FILES['image']), f'Only support .jpg, .jpeg or .png for image file, but got {self.path}'

        obj = load_image_obj(self.path, self.bytes)
        self.set_size(obj.width(), obj.height())
        self.item = obj
        self.view.scene().addPixmap(self.item)

class QMediaObj(QWidget):
    def __init__(self, path, bytes=None, fdir=None, view=None):
        super(QMediaObj, self).__init__()
        assert os.path.exists(path) or bytes

        self.fdir = fdir # 1st level folder
        supported_types = windowConfig.SUPPORTED_FILES

        if path.endswith('.gif'):
            self.obj = QGifObj(path, bytes, view)
        elif path.endswith(supported_types['video']):
            self.obj = QVideoObj(path, bytes, view)
            print('QVideoObj', view)
        elif path.endswith(supported_types['image']):
            self.obj = QImageObj(path, bytes, view)
        else:
            raise NotImplementedError(f'Only support {supported_types.keys()}, but got {path}')
        
        self.obj.load_media()
        for attr, value in self.obj.__dict__.items():
            setattr(self, attr, value)

    def show_in_view(self, qText):
        # qText = getQTitle(main_window, fpath, key)
        self.view.scene().addItem(qText)
        self.view.show()


def getQTitle(main_window, file_path, key, check_path_func=None):
    '''
    a typical path: dataset(folder)/method1(key)/xx.png 
    '''
    
    print('QMediaObj get title', file_path)
    # create new title
    # dataset = self.fdir.split(os.sep)[0]
    dataset = ''
    title_str = '\n'.join([dataset, key[:15], os.path.basename(file_path).split('.')[0]])
    
    check_path_func = os.path.exists if check_path_func is None else check_path_func
    if not check_path_func(file_path):
        title_str += f'\nDoes not exist :('
    else:
        title_str += f' ({main_window.currentIndex})'
    qText = QGraphicsTextItem(title_str)
    qText.setDefaultTextColor(Qt.red)
    if key in main_window.titles:
        # print(key, main_window.titles.keys(), qText.scale())
        qText.setScale(main_window.titles[key].scale())
        qText.setPos(main_window.titles[key].pos())
    else:
        qText.setScale(1.3)
    qText.setParentItem(None)
    main_window.titles[key] = qText
    # view.scene().addItem(qText)
    return qText