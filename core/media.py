import os
import cv2

from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt, QSizeF
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData

from config import windowConfig

def load_image(path=None, bytes=None, scale=True) -> QtGui.QPixmap:
    '''
    Args:
        path: str, load pixel map from a local image file path.
        bytes: bytes, load pixel map from image bytes.
        scale: bool, whether to scale the image according to config file. Default: True
    '''
    assert path or bytes, 'Either path or bytes should be provided'
    if path:
        pixmap = QtGui.QPixmap(path)
    else:
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(bytes)
    if scale:
        pixmap.scaledToWidth(windowConfig.IMG_SIZE_W)
    return pixmap

class QmediaObjHandler:
    def __init__(self) -> None:
        '''
        Args:
            type: str, options: ['image', 'video']
            loc: str, options: ['local', 'remote']
        '''
        self.load_func = {
            'img': load_image,
            'video': QUrl.fromLocalFile,
        }
        self.check_path_func = os.path.exists

        self.width = None
        self.height = None

    def request(self, view, path):
        if path.endswith('.mp4'):
            video_item = QGraphicsVideoItem()
            media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            # 设置 QGraphicsVideoItem 显示的内容
            media_player.setMedia(QMediaContent(self.load_func['video'](path)))
            view.scene().addItem(video_item)
            media_player.setVideoOutput(video_item)
            
            self.get_video_meta(path)
            w = windowConfig.IMG_SIZE_W
            video_item.setSize(QSizeF((self.width // w) * self.height, w))
            # Set loop count to -1 for infinite loop
            media_player.stateChanged.connect(lambda state: self.video_state_changed(state, media_player))
            media_player.play()
        else:
            assert path.endswith(('.jpg', '.png', '.jpeg')), f'Only support .jpg, .jpeg or .png for image file, but got {path}'
            pixmap = self.load_func['img'](path)
            self.width = pixmap.width()
            self.height = pixmap.height()
            view.scene().addPixmap(pixmap)

    def get_video_meta(self, path):
        video_capture = cv2.VideoCapture(path)
        self.width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_capture.release()
        print('video meta', self.width, self.height)

    def video_state_changed(self, state, media_player):
        if state == QMediaPlayer.StoppedState:
            # Restart the video when it reaches the end
            media_player.setPosition(0)
            media_player.play()
    
    def get_title(self, main_window, file_path, key):
        # create new title
        dataset = main_window.folderPaths[key].split(os.sep)[-2]
        title_str = '\n'.join([dataset, key[:15], os.path.basename(file_path).split('.')[0]])
        if not self.check_path_func(file_path):
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