import os
import cv2

from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt, QSizeF
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData

from config import windowConfig, sshConfig

def load_image(path=None, bytes=None, scale=True) -> QtGui.QPixmap:
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

def load_video(path, bytes=None) -> QUrl:
    '''Load QUrl from local video file path or file bytes.
    Args:
        file: str, load video from a local video file path.
    '''
    if not os.path.exists(path):
        assert bytes, f'File not provided and {path} not exists.'
        cache_dir = os.path.dirname(path)
        os.makedirs(cache_dir, exist_ok=True)
        # print('cache_dir', cache_dir)
        with open(path, "wb") as f:
            f.write(bytes)
            print('Caching video file to', path, '...')
    return QUrl.fromLocalFile(path)

class QMediaObj:
    def __init__(self, path, bytes=None, fdir=None):
        '''
        Args:
            type: str, options: ['image', 'video']
        '''
        self.fdir = fdir # 该媒体文件所属父级文件夹
        self.path = path
        self.bytes = bytes
        self.width = None
        self.height = None
        # Qmedia object: Qpixmap or QGraphicsVideoItem
        self.item = None

    def load_video(self):
        self.item = QGraphicsVideoItem()
        media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        qUrl = load_video(self.path, self.bytes)
        # 设置 QGraphicsVideoItem 显示的内容
        media_player.setMedia(QMediaContent(qUrl))
        media_player.setVideoOutput(self.item)

        # Get geometry information of the video.
        video_capture = cv2.VideoCapture(self.path)
        self.width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_capture.release()
        # print(self.path, self.width, self.height)
        
        w = windowConfig.IMG_SIZE_W
        self.item.setSize(QSizeF((self.width // w) * self.height, w))
        # Set loop count to -1 for infinite loop
        media_player.stateChanged.connect(lambda state: self.video_state_changed(state, media_player))
        media_player.play()
    
    def video_state_changed(self, state, player):
        '''Set infinite loop playback for video.'''
        if state == QMediaPlayer.StoppedState:
            # Restart the video when it reaches the end
            player.setPosition(0)
            player.play()

    def load_image(self):
        assert self.path.endswith(('.jpg', '.png', '.jpeg')), f'Only support .jpg, .jpeg or .png for image file, but got {self.path}'
        
        pixmap = load_image(self.path, self.bytes)
        self.width, self.height = pixmap.width(), pixmap.height()
        self.item = pixmap

    def get_title(self, main_window, file_path, key, check_path_func=None):
        '''
        a typical path: dataset(folder)/method1(key)/xx.png 
        '''
        # create new title
        # print('get title', file_path)
        dataset = self.fdir.split(os.sep)[0]
        title_str = '\n'.join([dataset, key[:15], os.path.basename(file_path).split('.')[0]])
        
        check_path_func = os.path.exists if check_path_func is None else check_path_func
        if not check_path_func(file_path):
            title_str += f'\nDoes not exist :('
        else:
            title_str += f' ({main_window.currentIndex})'
        qText = QGraphicsTextItem(title_str)
        qText.setDefaultTextColor(Qt.red)
        if key in main_window.titles:
            qText.setScale(main_window.titles[key].scale())
            qText.setPos(main_window.titles[key].pos())
        else:
            qText.setScale(1.3)
        main_window.titles[key] = qText
        # view.scene().addItem(qText)
        return qText

    def __del__(self):
        del self.item

def saveMediaBytes(path, file_bytes, fdir):
    '''Save media bytes to local path.'''
    os.makedirs(fdir, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(file_bytes)

def requestQMedia(path, file_bytes=None, fdir=None):
    '''Request media object from local or remote. Support image and video media reading.'''
    # print(path, file_bytes)
    qMedia = QMediaObj(path, file_bytes, fdir)
    if path.endswith('.mp4'):
        qMedia.load_video()
    elif path.endswith(('.jpg', '.png', '.jpeg')):
        qMedia.load_image()
    else:
        raise NotImplementedError(f'Only support .jpg, .jpeg, .png or .mp4 for image or video file, but got {path}')
    return qMedia
    
    