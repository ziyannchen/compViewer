# compViewer
> compViewer – An utility to effortlessly navigate and compare multiple media windows, e.g. multiple baselines. \
compViewer - 一个提供**多个不同baseline**进行方便地网格状浏览的工具。

Tech stack:
- PyQt5 (for UI)
- paramiko (for remote access)

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
### 基本设置

在`config`下的.yaml文件中填写等基础设置。

- 窗口设置`window.yaml`

    p.s. 可以只填写IMG_SIZE_W，这个大小最好按照图片实际的宽来填写，因为该大小会影响grid中显示的图像分辨率。

- ssh远程服务器设置`ssh.yaml`

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

- **Add folder**：选中一个父文件夹，将同时load所有的子文件夹。
默认显示第一张。

- **Del folder**：每次删除文件夹列表中的最后一项。（这个功能现在可能没啥用）

### 图片操作

- **图片缩放**：鼠标向上 / 下滚动
(支持所有图片同时缩放、移动：在非窗口区域操作鼠标)

- **图像局部区域移动**：鼠标左键点击+移动

- **图片切换**
    - **上一张**：键盘A / 键盘W
    - **下一张**：键盘S / 键盘D / 键盘空格space

### 索引GoTo

- **by Index**：load进来的所有图片先按照名字进行排序(natsorted)，index为排序后的index
- **by Name**: 模糊查找，跳转到第一个满足条件的

### 远程服务器访问
在ssh.yaml的test_host1配置你的服务器信息，出于安全考虑，目前仅支持公钥访问。

连接成功后在挑出来的对话框中的textEdit输入你想要对比的文件夹路径(用英文分号;分割)，将自动加载显示。


#### Special Features
- Local cache：在请求远程资源显示到窗口中时，将自动缓存到本地ssh.yaml中配置的CacheDir，来节约ssh传输带来的开销。

#### 可能的异常
目前可能因为多文件远程传输，会存在一些小问题，但不妨碍正常的浏览。
- 加载卡顿 If you feel an obvious pause when shifting to another view, it's most probably from the remote ssh file-loading costs, which usually takes 1s for each video.

- 空白的媒体窗口视图 If you encounter empty unit media window view(s) but not due to missing media source, try switching to another view and back to check if it's normal (Bug not found currenlt).