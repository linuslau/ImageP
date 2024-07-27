import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
import numpy as np
from pyqtgraph import PlotWidget, mkPen, ImageItem
import pyqtgraph as pg

class DynamicLinePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.plotWidget = PlotWidget(self)
        self.setCentralWidget(self.plotWidget)
        self.plotWidget.setMouseTracking(True)

        self.start_point = None
        self.dynamic_line = None
        self.lines = []
        self.initial_point = None
        self.threshold = 20  # 设置适合图像处理应用的阈值

        self.plotWidget.plotItem.showGrid(True, True, 0.5)
        self.plotWidget.setBackground('w')

        # 添加一个菜单栏，用于打开图片
        openFile = QAction('Open Image', self)
        openFile.triggered.connect(self.open_image)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(openFile)

        self.plotWidget.scene().sigMouseMoved.connect(self.mouse_moved)
        self.plotWidget.scene().sigMouseClicked.connect(self.mouse_clicked)

    def open_image(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)
        if fileName:
            self.plotWidget.plotItem.clear()
            image = QImage(fileName)
            if image.isNull():
                print(f"Failed to load image: {fileName}")
                return
            image = image.convertToFormat(QImage.Format.Format_RGB32)
            width, height = image.width(), image.height()
            ptr = image.bits()
            ptr.setsize(image.byteCount())
            arr = np.array(ptr).reshape((height, width, 4))
            arr = arr[:, :, :3]  # Drop the alpha channel
            arr = np.flip(arr, axis=0)  # Flip vertically

            img_item = ImageItem(arr)
            self.plotWidget.addItem(img_item)
            print(f"Opened image: {fileName}")

    def mouse_clicked(self, event):
        if event.button() == Qt.LeftButton:
            mouse_point = self.plotWidget.plotItem.vb.mapSceneToView(event.scenePos())
            new_point = (mouse_point.x(), mouse_point.y())
            print(f"Clicked point: {new_point}")

            if self.start_point is None:
                self.start_point = new_point
                self.initial_point = self.start_point
                self.plotWidget.plot([self.start_point[0]], [self.start_point[1]], pen=None, symbol='o')
                print(f"Initial point set: {self.initial_point}")
            else:
                if self.is_close_to_initial_point(new_point):
                    print(f"Ending round at point: {new_point}")
                    self.plotWidget.plot([new_point[0]], [new_point[1]], pen=None, symbol='o')
                    self.end_current_round()
                    return
                else:
                    self.plotWidget.plot([self.start_point[0], new_point[0]], [self.start_point[1], new_point[1]], pen=mkPen(color='r', width=2))
                    self.lines.append((self.start_point, new_point))
                    self.start_point = new_point
                    self.plotWidget.plot([self.start_point[0]], [self.start_point[1]], pen=None, symbol='o')
                    print(f"New line drawn to: {new_point}")

    def mouse_moved(self, event):
        if self.start_point is not None:
            mouse_point = self.plotWidget.plotItem.vb.mapSceneToView(event)
            end_point = (mouse_point.x(), mouse_point.y())

            if self.dynamic_line is not None:
                self.plotWidget.removeItem(self.dynamic_line)

            self.dynamic_line = pg.PlotDataItem(
                [self.start_point[0], end_point[0]], [self.start_point[1], end_point[1]],
                pen=mkPen(color='r', width=2)
            )
            self.plotWidget.addItem(self.dynamic_line)

    def is_close_to_initial_point(self, point, threshold=20):
        """判断当前点是否接近初始点"""
        distance = ((point[0] - self.initial_point[0]) ** 2 + (point[1] - self.initial_point[1]) ** 2) ** 0.5
        print(f"Distance from initial point: {distance}")
        return distance < threshold

    def end_current_round(self):
        """结束当前轮绘制"""
        self.start_point = None
        self.dynamic_line = None
        self.initial_point = None
        # 这里我们不清除已绘制的线条，只是结束当前轮次的绘制

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = DynamicLinePlot()
    mainWin.show()
    sys.exit(app.exec_())
