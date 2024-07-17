# compViewer
An utility to navigate and compare multiple media windows, e.g. multiple baselines. \
提供**多个不同baselines**进行方便地网格状浏览的工具，支持放大缩小，视图组切换。


> Application scenes 1) user study, 2) paper image selection, 3) expriment image checking.

<img src="figs/demo.png"></img>

## Features

- **媒体支持**
    - 图片
    - 视频
- **access**
    - 本地文件访问
    - 远程服务器文件访问(同时进行本地文件缓存)
- **索引**
    - 根据index索引
    - 根据文件名模糊查找
- **保存**
    - 保存当前视图所有图片到单个文件夹

## Instructions
### Run
```python
python main.py
```

### 基本设置

在`config`下的.yaml文件中填写等基础设置。

- 窗口设置`window.yaml`

    p.s. MEDIA_W/MEDIA_H表示的是grid中显示的图像分辨率，缩放操作会影响原始的分辨率，目前暂不支持调整，这个大小默认为图片实际的宽/高来展示。

> 这里grid大小和图像大小不一样，grid会自动随着整个程序框的大小来调整；但图像缩放的时候会有损，所以默认原图大小更好。

### 打开/删除文件夹
菜单File
- **Load All**: 如果你有已经准备好的如下所示的文件树，即一个文件夹表示一个数据集，其中的子文件夹表示所有的baseline，每个子文件夹中的数据名称一致，那么可以直接用load all来将lfw_face这个文件夹一次性load进来。(如果存在不一致的情况，软件可以兼容，但是无法同时显示所有baseline进行比较。)

```
lfw_face
├── lq
    ├── 1.png
    └── 2.mp4
├── CodeFormer
    ├── 1.png
    └── 2.mp4
├── DiffBIR
    ├── 1.png
    └── 2.mp4
└── PGDiff
    ├── 1.png
    └── 2.mp4
```
> 最好能保证所有baseline文件夹中的文件名称及后缀都是一致的，这样不容易出错。
目前支持的文件类型：['jpg', 'jpeg', 'png', 'bmp'],['mp4', 'avi', 'mov', 'gif'].

> 目前靠文件夹最后一级名称来区分不同的baseline，因此需要保证不同的baseline的路径最后一级的名字不同。

- **Add folder**：选中一个父文件夹，将同时load所有的子文件夹。
默认显示第一张。

- **Del folder**：每次删除文件夹列表中的最后一项。（这个功能现在可能没啥用）

### 图片操作

- **图片缩放**：鼠标向上 / 下滚动

- **图像区域拖动**：鼠标左键点击+拖动

> 1) 在非图像区域操作：所有图片同时缩放、拖动；
> 2) 在单个图像区域操作：单个图像缩放、拖动。

- **图片切换**
    - **上一张**：键盘A / 键盘W
    - **下一张**：键盘S / 键盘D / 键盘空格space

### 索引GoTo

- **by Index**：load进来的所有图片先按照名字进行排序(natsorted)，index为排序后的index
- **by Name**: 模糊查找，跳转到第一个满足条件的

### 保存
- 保存当前组图像到指定文件夹，用于写论文找图一键拿到多个baseline的图。

### 远程服务器访问
- 服务器信息配置：vscode的ssh连接类似，自动加载`~/.ssh/config`路径的服务器设置。
- 登陆验证：目前仅支持公钥验证模式，默认加载`~/.ssh/id_rsa`私钥信息。

- 远程文件夹加载：连接成功后在跳出来的对话框中输入你想要对比的服务器文件夹路径(用英文分号`;`分割)，将自动加载显示并缓存到本地文件夹。


#### Special Features
- Local cache：在请求远程资源显示到窗口中时，将自动缓存到本地ssh.yaml中配置的CacheDir(默认是项目文件夹下的./.cache)，来节约ssh传输带来的开销。

#### 可能的异常
目前可能因为多文件远程传输，会存在一些小问题，但不妨碍正常的浏览。
- 加载卡顿 If you feel an obvious pause when shifting to another view, it's most probably from costs of the remote ssh file-loading and cacing, which usually takes about 1s for a 512*512 video.

- 空白的媒体窗口视图 If you encounter empty unit media window view(s) but not due to missing media source, try switching to another view and back to check if it's normal (Bug not found currenlt).


# Development-related

## build
### .exe
```shell
pyinstaller --onefile --windowed main.py
```

### .dmg
```shell
pyinstaller --onefile --windowed main.py
cd dist
hdiutil create -volname compViewer -srcfolder main.app -ov -format UDZO compViewer.dmg
```


## pyqt ui designer
```shell
# pyqt designer
designer

# compile ui file
pyuic5 -o ui/base.py ui/base.ui
```

## Tech stack:
- PyQt5
- paramiko

<!-- ```
pyinstaller -F ui/main.py
``` -->