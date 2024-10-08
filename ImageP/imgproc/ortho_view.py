from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np
import sys

class OrthogonalViewWidget(QWidget):
    def __init__(self, image_data):
        super().__init__()

        self.image_data = image_data  # 3D图像数据
        self.shape = image_data.shape  # 获取图像的实际形状 (z, y, x)

        # 获取图像中心的索引
        self.center_x_idx = self.shape[2] // 2
        self.center_y_idx = self.shape[1] // 2
        self.center_z_idx = self.shape[0] // 2
        self.mouse_pressed = False  # 标记鼠标是否按下

        # 创建显示正交视图的图形布局
        self.xy_widget = pg.GraphicsLayoutWidget()
        self.xz_widget = pg.GraphicsLayoutWidget()
        self.yz_widget = pg.GraphicsLayoutWidget()

        # 为每个视图创建ImageItem
        self.xy_image = pg.ImageItem()
        self.xz_image = pg.ImageItem()
        self.yz_image = pg.ImageItem()

        # 创建十字线
        self.crosshair_xy = pg.InfiniteLine(angle=0, pen=pg.mkPen('r'))
        self.crosshair_xz = pg.InfiniteLine(angle=0, pen=pg.mkPen('r'))
        self.crosshair_yz = pg.InfiniteLine(angle=0, pen=pg.mkPen('r'))

        self.crosshair_xy_v = pg.InfiniteLine(angle=90, pen=pg.mkPen('r'))
        self.crosshair_xz_v = pg.InfiniteLine(angle=90, pen=pg.mkPen('r'))
        self.crosshair_yz_v = pg.InfiniteLine(angle=90, pen=pg.mkPen('r'))

        # 将ImageItems添加到图项
        self.xy_plot = pg.PlotItem()
        self.xz_plot = pg.PlotItem()
        self.yz_plot = pg.PlotItem()

        # 反转Y轴，使得(0, 0)在左上角
        self.xy_plot.invertY(True)
        self.xz_plot.invertY(True)
        self.yz_plot.invertY(True)

        # 获取实际的图像长宽比
        xy_aspect = self.shape[2] / self.shape[1]  # XY视图：X轴长度 / Y轴长度
        xz_aspect = self.shape[2] / self.shape[0]  # XZ视图：X轴长度 / Z轴长度
        yz_aspect = self.shape[1] / self.shape[0]  # YZ视图：Y轴长度 / Z轴长度

        # 根据长宽比锁定视图比例
        self.xy_plot.getViewBox().setAspectLocked(True, xy_aspect)
        self.xz_plot.getViewBox().setAspectLocked(True, xz_aspect)
        self.yz_plot.getViewBox().setAspectLocked(True, yz_aspect)

        self.xy_plot.addItem(self.xy_image)
        self.xz_plot.addItem(self.xz_image)
        self.yz_plot.addItem(self.yz_image)

        # 隐藏底部X轴，并将X轴刻度移动到顶部
        self.xy_plot.getAxis('bottom').setStyle(showValues=False)  # 隐藏底部的X轴刻度
        self.xy_plot.showAxis('top')  # 显示顶部X轴
        self.xy_plot.getAxis('top').setStyle(showValues=True)  # 显示顶部的X轴刻度

        # 隐藏底部X轴，并将X轴刻度移动到顶部
        self.xz_plot.getAxis('bottom').setStyle(showValues=False)  # 隐藏底部的X轴刻度
        self.xz_plot.showAxis('top')  # 显示顶部X轴
        self.xz_plot.getAxis('top').setStyle(showValues=True)  # 显示顶部的X轴刻度

        # 隐藏底部X轴，并将X轴刻度移动到顶部
        self.yz_plot.getAxis('bottom').setStyle(showValues=False)  # 隐藏底部的X轴刻度
        self.yz_plot.showAxis('top')  # 显示顶部X轴
        self.yz_plot.getAxis('top').setStyle(showValues=True)  # 显示顶部的X轴刻度

        # 将十字线添加到相应视图
        self.xy_plot.addItem(self.crosshair_xy)
        self.xy_plot.addItem(self.crosshair_xy_v)

        self.xz_plot.addItem(self.crosshair_xz)
        self.xz_plot.addItem(self.crosshair_xz_v)

        self.yz_plot.addItem(self.crosshair_yz)
        self.yz_plot.addItem(self.crosshair_yz_v)

        # 设置各个视图的大小（调大）
        self.xy_widget.setMinimumSize(700, 700)
        self.xz_widget.setMinimumSize(700, 700)
        self.yz_widget.setMinimumSize(700, 700)

        self.xy_widget.addItem(self.xy_plot)
        self.xz_widget.addItem(self.xz_plot)
        self.yz_widget.addItem(self.yz_plot)

        # 布局修改：将三个视图横向排列
        layout = QHBoxLayout()  # 改为水平布局

        # 分别为每个视图创建垂直布局，将标签放在视图上方
        xy_layout = QVBoxLayout()
        xy_label = QLabel("XY视图")
        xy_layout.addWidget(xy_label)
        xy_layout.addWidget(self.xy_widget)

        xz_layout = QVBoxLayout()
        xz_label = QLabel("XZ视图")
        xz_layout.addWidget(xz_label)
        xz_layout.addWidget(self.xz_widget)

        yz_layout = QVBoxLayout()
        yz_label = QLabel("YZ视图")
        yz_layout.addWidget(yz_label)
        yz_layout.addWidget(self.yz_widget)

        layout.addLayout(xy_layout)
        layout.addLayout(xz_layout)
        layout.addLayout(yz_layout)

        self.setLayout(layout)

        # 初始化正交视图
        # self.update_orthogonal_views(0, 0, 0)
        print(f"Initializing orthogonal views with center: x_idx={self.center_x_idx}, y_idx={self.center_y_idx}, z_idx={self.center_z_idx}")
        self.update_orthogonal_views(self.center_x_idx, self.center_y_idx, self.center_z_idx)

        # 监听鼠标点击事件
        self.xy_plot.scene().sigMouseClicked.connect(self.on_mouse_click)
        self.xz_plot.scene().sigMouseClicked.connect(self.on_mouse_click)
        self.yz_plot.scene().sigMouseClicked.connect(self.on_mouse_click)

        # 监听鼠标事件：按下、移动、释放
        self.xy_plot.scene().installEventFilter(self)
        self.xz_plot.scene().installEventFilter(self)
        self.yz_plot.scene().installEventFilter(self)

        # 居中显示窗口
        self.showEvent(None)  # 使用showEvent

        # 启动时最大化窗口
        # self.showMaximized()

    def showEvent(self, event):
        """在窗口显示时进行居中操作"""
        self.center_window()

    def center_window(self):
        # 获取主屏幕的分辨率
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # 获取窗口的几何尺寸
        window_geometry = self.frameGeometry()

        # 将窗口移动到屏幕中心
        screen_center = screen_geometry.center()
        window_geometry.moveCenter(screen_center)

        # 将窗口移动到正确的中心位置
        self.move(window_geometry.topLeft())

    def update_crosshairs(self, x_idx, y_idx, z_idx):
        """在各个视图中更新十字线位置"""
        print(f"\nUpdating crosshairs to: x_idx={x_idx}, y_idx={y_idx}, z_idx={z_idx}")
        self.crosshair_xy.setPos(y_idx)
        self.crosshair_xz.setPos(z_idx)
        self.crosshair_yz.setPos(y_idx)

        self.crosshair_xy_v.setPos(x_idx)
        self.crosshair_xz_v.setPos(x_idx)
        self.crosshair_yz_v.setPos(z_idx)

    def update_orthogonal_views(self, x_idx, y_idx, z_idx, update_xy=True, update_xz=True, update_yz=True):
        """更新正交视图（XY, XZ, YZ平面），使用当前截面"""

        # 确保索引不超出图像范围
        print(f"\nReceived indices for update: x_idx={x_idx}, y_idx={y_idx}, z_idx={z_idx}")
        x_idx = np.clip(x_idx, 0, self.shape[2] - 1)
        y_idx = np.clip(y_idx, 0, self.shape[1] - 1)
        z_idx = np.clip(z_idx, 0, self.shape[0] - 1)
        print(f"Clipped indices: x_idx={x_idx}, y_idx={y_idx}, z_idx={z_idx}")

        if update_xy:
            # XY平面（俯视图，Z恒定）
            xy_slice = self.image_data[z_idx, :, :]
            print(f"Updating XY view at z_idx={z_idx}")
            # self.xy_image.setImage(np.rot90(xy_slice, 1))  # 纠正图像显示方向
            self.xy_image.setImage(xy_slice)  # 纠正图像显示方向

        if update_xz:
            # XZ平面（垂直剖面，Y恒定）
            xz_slice = np.flip(self.image_data[:, y_idx, :], axis=1)  # 水平翻转XZ切片
            print(f"Updating XZ view at y_idx={y_idx}")
            self.xz_image.setImage(np.rot90(xz_slice, 1))  # 纠正图像显示方向

        if update_yz:
            # YZ平面（垂直剖面，X恒定）
            yz_slice = self.image_data[:, :, x_idx]
            print(f"Updating YZ view at x_idx={x_idx}")
            self.yz_image.setImage(np.rot90(yz_slice, 0))  # 纠正图像显示方向

        # 更新十字线位置
        self.update_crosshairs(x_idx, y_idx, z_idx)

    def apply_view_all_to_all(self):
        """同步执行所有视图的 View All（自动缩放）"""
        self.xy_plot.getViewBox().autoRange()  # 自动调整XY视图
        self.xz_plot.getViewBox().autoRange()  # 自动调整XZ视图
        self.yz_plot.getViewBox().autoRange()  # 自动调整YZ视图

    # 事件过滤器中，明确禁用左击拖动
    def eventFilter(self, obj, event):
        """处理鼠标事件"""
        # 鼠标双击事件，执行同步的 View All 操作
        if event.type() == pg.QtCore.QEvent.GraphicsSceneMouseDoubleClick:
            # 双击时执行 View All 操作
            self.apply_view_all_to_all()  # 调用同步 View All 函数
            return True  # 表示事件已经处理，阻止进一步传播

        if event.type() == pg.QtCore.QEvent.GraphicsSceneWheel:
            # 获取滚动的角度，直接使用 event.delta() 而不是 event.angleDelta().y()
            delta = event.delta()

            # 将滚动的比例应用到所有视图，保持同步
            scale_factor = 1.1 if delta > 0 else 0.9

            # 应用缩放到每个视图
            self.xy_plot.getViewBox().scaleBy((scale_factor, scale_factor))
            self.xz_plot.getViewBox().scaleBy((scale_factor, scale_factor))
            self.yz_plot.getViewBox().scaleBy((scale_factor, scale_factor))

            return True  # 处理完事件后返回 True

        if event.type() == pg.QtCore.QEvent.GraphicsSceneMousePress:
            if event.button() == Qt.LeftButton:
                # 鼠标左键按下，标记为 True
                self.mouse_pressed = True
                # 禁用左键拖动功能
                if obj == self.xy_plot.scene():
                    self.xy_plot.getViewBox().setMouseEnabled(x=False, y=False)
                elif obj == self.xz_plot.scene():
                    self.xz_plot.getViewBox().setMouseEnabled(x=False, y=False)
                elif obj == self.yz_plot.scene():
                    self.yz_plot.getViewBox().setMouseEnabled(x=False, y=False)
            elif event.button() == Qt.RightButton:
                # 鼠标右键按下，启用拖动功能
                if obj == self.xy_plot.scene():
                    self.xy_plot.getViewBox().setMouseEnabled(x=True, y=True)
                elif obj == self.xz_plot.scene():
                    self.xz_plot.getViewBox().setMouseEnabled(x=True, y=True)
                elif obj == self.yz_plot.scene():
                    self.yz_plot.getViewBox().setMouseEnabled(x=True, y=True)

        elif event.type() == pg.QtCore.QEvent.GraphicsSceneMouseRelease:
            if event.button() == Qt.LeftButton:
                # 鼠标左键释放，允许其他功能
                self.mouse_pressed = False
                if obj == self.xy_plot.scene():
                    self.xy_plot.getViewBox().setMouseEnabled(x=True, y=True)
                elif obj == self.xz_plot.scene():
                    self.xz_plot.getViewBox().setMouseEnabled(x=True, y=True)
                elif obj == self.yz_plot.scene():
                    self.yz_plot.getViewBox().setMouseEnabled(x=True, y=True)

        elif event.type() == pg.QtCore.QEvent.GraphicsSceneMouseMove and self.mouse_pressed:
            # 鼠标移动逻辑保持不变，只处理十字线移动
            pos = event.scenePos()
            if obj == self.xy_plot.scene():
                view_pos = self.xy_plot.vb.mapSceneToView(pos)
                x_idx = int(view_pos.x())
                y_idx = int(view_pos.y())
                z_idx = int(self.crosshair_xz.pos()[1])
                self.update_orthogonal_views(x_idx, y_idx, z_idx, update_xy=False)
                # self.update_crosshairs(x_idx, y_idx, z_idx)
            elif obj == self.xz_plot.scene():
                view_pos = self.xz_plot.vb.mapSceneToView(pos)
                x_idx = int(view_pos.x())
                z_idx = int(view_pos.y())
                y_idx = int(self.crosshair_yz.pos()[1])
                self.update_orthogonal_views(x_idx, y_idx, z_idx, update_xz=False)
                # self.update_crosshairs(x_idx, y_idx, z_idx)
            elif obj == self.yz_plot.scene():
                view_pos = self.yz_plot.vb.mapSceneToView(pos)
                y_idx = int(view_pos.y())
                z_idx = int(view_pos.x())
                x_idx = int(self.crosshair_xy_v.pos()[0])
                self.update_orthogonal_views(x_idx, y_idx, z_idx, update_yz=False)
                # self.update_crosshairs(x_idx, y_idx, z_idx)

        return super().eventFilter(obj, event)

    def on_mouse_click(self, event):
        """根据鼠标点击更新十字线和视图"""
        pos = event.scenePos()
        print(f"\n\nMouse clicked at position: {pos}")

        # 获取点击位置并映射到相应视图的坐标
        if self.xy_plot.sceneBoundingRect().contains(pos) and self.xy_plot.isUnderMouse():
            view_pos = self.xy_plot.vb.mapSceneToView(pos)
            x_idx = int(view_pos.x())  # 交换 X 和 Y，使得点击的横向移动和纵向移动正确
            y_idx = int(view_pos.y())  # 点击右移对应 Y 轴，点击下移对应 X 轴
            z_idx = int(self.crosshair_xz.pos()[1])  # 保持XZ平面上的Z不变

            print(f"Updating after XY plot click: x_idx={x_idx}, y_idx={y_idx}, z_idx={z_idx}")
            # 只更新 XZ 和 YZ 图像，不更新 XY 图像
            self.update_orthogonal_views(x_idx, y_idx, z_idx, update_xy=False)

        elif self.xz_plot.sceneBoundingRect().contains(pos) and self.xz_plot.isUnderMouse():
            view_pos = self.xz_plot.vb.mapSceneToView(pos)
            x_idx = int(view_pos.x())  # 点击左右移动对应 Z 轴
            z_idx = int(view_pos.y())  # 点击上下移动对应 X 轴
            y_idx = int(self.crosshair_yz.pos()[1])  # 保持YZ平面上的Y不变

            print(f"Updating after XZ plot click: x_idx={x_idx}, y_idx={y_idx}, z_idx={z_idx}")
            # 只更新 XY 和 YZ 图像，不更新 XZ 图像
            self.update_orthogonal_views(x_idx, y_idx, z_idx, update_xz=False)

        elif self.yz_plot.sceneBoundingRect().contains(pos) and self.yz_plot.isUnderMouse():
            view_pos = self.yz_plot.vb.mapSceneToView(pos)
            y_idx = int(view_pos.y())  # 点击上下移动对应 Y 轴
            z_idx = int(view_pos.x())  # 点击左右移动对应 Z 轴
            x_idx = int(self.crosshair_xy_v.pos()[0])  # 保持XY平面上的X不变

            print(f"Updating after YZ plot click: x_idx={x_idx}, y_idx={y_idx}, z_idx={z_idx}")
            # 只更新 XY 和 XZ 图像，不更新 YZ 图像
            self.update_orthogonal_views(x_idx, y_idx, z_idx, update_yz=False)

        else:
            print("Error: Clicked on an unknown view")
            return


if __name__ == '__main__':
    app = QApplication([])  # 创建 PyQt 应用程序

    params = {
        'image_type': '8-bit',  # 硬编码的图像类型
        'width': 384,  # 图像宽度
        'height': 384,  # 图像高度
        'offset': 0,  # 起始偏移
        'num_images': 384,  # 图像数量
        'gap': 0,  # 图像之间的间隙
        'white_zero': False,  # 白色是否为零
        'little_endian': False,  # 字节顺序
        'open_all_files': False,  # 是否打开文件夹中的所有文件
        'virtual_stack': False  # 是否使用虚拟栈
    }

    file_path = "../maotai_384x384x384.raw"  # 文件路径，确保文件在同一目录下，或提供完整路径
    layers = params['num_images']
    width = params['width']
    height = params['height']
    shape = (layers, height, width)
    dtype = np.float32

    image = np.fromfile(file_path, dtype=dtype)

    image = image.byteswap().newbyteorder()  # Handle little-endian data

    image = image.reshape(shape)
    # 创建正交视图窗口并显示
    widget = OrthogonalViewWidget(image)
    widget.show()

    sys.exit(app.exec_())  # 启动事件循环
