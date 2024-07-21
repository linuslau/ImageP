import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseMode(self.RectMode)
        self.start_pos = None
        self.rect_item = None

    def mousePressEvent(self, event):
        pos = event.pos()
        if self.rect_item is not None:
            self.removeItem(self.rect_item)
            self.rect_item = None

        self.start_pos = self.mapToView(pos)
        self.rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, self.start_pos))
        self.rect_item.setPen(pg.mkPen(color='r', width=2))
        self.addItem(self.rect_item)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.rect_item is not None and self.start_pos is not None:
            current_pos = self.mapToView(event.pos())
            rect = QtCore.QRectF(self.start_pos, current_pos).normalized()
            self.rect_item.setRect(rect)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        event.accept()


class ImageWithRect(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQtGraph Example: Image with Rectangle')
        self.view = CustomViewBox()
        self.view.setAspectLocked(True)

        # 在窗口中添加一个图像视图
        self.plot_item = pg.PlotItem(viewBox=self.view)
        self.addItem(self.plot_item)

        # 读取并显示图像
        self.image = np.random.rand(100, 100) * 255  # 这里用随机数据模拟图片，可以替换为你自己的图片数据
        self.img = pg.ImageItem(self.image)
        self.plot_item.addItem(self.img)


# 创建一个应用程序实例
app = QtWidgets.QApplication([])

# 创建并显示窗口
win = ImageWithRect()
win.show()

# 运行应用程序
if __name__ == '__main__':
    QtWidgets.QApplication.instance().exec_()
