import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np
from PIL import Image


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseMode(self.RectMode)
        self.start_pos = None
        self.rect_item = None
        self.dragging = False
        self.resizing = False
        self.resize_start_pos = None
        self.rect_initial = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and self.rect_item is not None:
            pos = event.pos()
            view_pos = self.mapToView(pos)
            rect = self.rect_item.rect()
            if rect.contains(view_pos):
                self.showContextMenu(event)
                return

        pos = event.pos()
        view_pos = self.mapToView(pos)

        if self.rect_item is not None:
            rect = self.rect_item.rect()
            if self.isNearEdge(view_pos, rect):
                self.start_pos = view_pos
                self.resizing = True
                self.rect_initial = rect
                self.resize_start_pos = self.start_pos
            elif rect.contains(view_pos):
                self.start_pos = view_pos
                self.dragging = True
            else:
                self.removeItem(self.rect_item)
                self.start_pos = self.mapToView(pos)
                self.rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, self.start_pos))
                self.rect_item.setPen(pg.mkPen(color='r', width=2))
                self.addItem(self.rect_item)
        else:
            self.start_pos = self.mapToView(pos)
            self.rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, self.start_pos))
            self.rect_item.setPen(pg.mkPen(color='r', width=2))
            self.addItem(self.rect_item)

        event.accept()

    def mouseMoveEvent(self, event):
        if self.rect_item is not None and self.start_pos is not None:
            current_pos = self.mapToView(event.pos())

            if self.dragging:
                dx = current_pos.x() - self.start_pos.x()
                dy = current_pos.y() - self.start_pos.y()
                rect = self.rect_item.rect()
                rect.moveTopLeft(QtCore.QPointF(rect.left() + dx, rect.top() + dy))
                self.rect_item.setRect(rect)
                self.start_pos = current_pos
            elif self.resizing:
                dx = current_pos.x() - self.resize_start_pos.x()
                dy = current_pos.y() - self.resize_start_pos.y()
                new_rect = QtCore.QRectF(self.rect_initial)
                new_rect.setBottomRight(QtCore.QPointF(new_rect.right() + dx, new_rect.bottom() + dy))
                self.rect_item.setRect(new_rect)
            else:
                rect = QtCore.QRectF(self.start_pos, current_pos).normalized()
                self.rect_item.setRect(rect)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        self.dragging = False
        self.resizing = False
        self.rect_initial = None
        self.resize_start_pos = None
        event.accept()

    def isNearEdge(self, pos, rect):
        edge_tolerance = 10
        near_left = abs(pos.x() - rect.left()) < edge_tolerance
        near_right = abs(pos.x() - rect.right()) < edge_tolerance
        near_top = abs(pos.y() - rect.top()) < edge_tolerance
        near_bottom = abs(pos.y() - rect.bottom()) < edge_tolerance

        return near_left or near_right or near_top or near_bottom

    def showContextMenu(self, event):
        menu = QtWidgets.QMenu()
        row_properties_action = menu.addAction("ROW Properties")
        row_properties_action.triggered.connect(self.showRowPropertiesDialog)
        menu.exec_(event.screenPos())

    def showRowPropertiesDialog(self):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("ROW Properties")

        layout = QtWidgets.QFormLayout()

        labels = ["Property 1", "Property 2", "Property 3", "Property 4", "Property 5"]
        self.inputs = []

        for label in labels:
            input_field = QtWidgets.QLineEdit()
            layout.addRow(QtWidgets.QLabel(label), input_field)
            self.inputs.append(input_field)

        buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        button_box = QtWidgets.QDialogButtonBox(buttons)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addRow(button_box)
        dialog.setLayout(layout)

        if dialog.exec_():
            values = [input_field.text() for input_field in self.inputs]
            print("Accepted with values:", values)
        else:
            print("Cancelled")


class ImageWithRect(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQtGraph Example: Image with Rectangle')
        self.view = CustomViewBox()
        self.view.setAspectLocked(True)

        # 在窗口中添加一个图像视图
        self.plot_item = pg.PlotItem(viewBox=self.view)
        self.addItem(self.plot_item)

        # 读取并显示指定图像
        image_path = 'boats_720x576_8bits.raw'  # 替换为你的图像路径
        image = self.load_raw_image(image_path, (576, 720))

        # 旋转图像数组90度，纠正方向
        image = np.rot90(image, k=3)  # 旋转270度，相当于顺时针旋转90度

        self.img = pg.ImageItem(image)
        self.plot_item.addItem(self.img)

    def load_raw_image(self, file_path, shape):
        # 读取raw图像文件
        image = np.fromfile(file_path, dtype=np.uint8)
        image = image.reshape(shape)
        return image


# 创建一个应用程序实例
app = QtWidgets.QApplication([])

# 创建并显示窗口
win = ImageWithRect()
win.show()

# 运行应用程序
if __name__ == '__main__':
    QtWidgets.QApplication.instance().exec_()
