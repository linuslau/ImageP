import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
import numpy as np
from pyqtgraph import PlotWidget, mkPen, ImageItem
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseMode(self.RectMode)
        self.start_pos = None
        self.shape_item = None
        self.dragging = False
        self.resizing = False
        self.resize_start_pos = None
        self.shape_initial = None
        self.image_data = None
        self.image_item = None
        self.control_points = []
        self.control_items = []
        self.dragging_control_point = None
        self.hovering_control_point = None
        self.setMenuEnabled(True)
        self.shape_type = "dynamic_line"  # "rectangle", "ellipse", "polygon", "dynamic_line"
        self.polygon_points = []
        self.temp_line = None
        self.clear_previous_lines = True  # Flag to control whether to clear previous lines

    def setImageData(self, image_data, image_item):
        self.image_data = image_data
        self.image_item = image_item

    def updateControlPoints(self):
        for item in self.control_items:
            self.removeItem(item)
        self.control_items = []

        if self.shape_item is None:
            self.control_points = []
            return

        if self.shape_type == "polygon":
            self.control_points = self.polygon_points
        else:
            rect = self.shape_item.rect()
            x1, y1 = rect.topLeft().x(), rect.topLeft().y()
            x2, y2 = rect.bottomRight().x(), rect.bottomRight().y()
            self.control_points = [
                QtCore.QPointF(x1, y1),  # Top-left
                QtCore.QPointF(x2, y1),  # Top-right
                QtCore.QPointF(x1, y2),  # Bottom-left
                QtCore.QPointF(x2, y2),  # Bottom-right
                QtCore.QPointF((x1 + x2) / 2, y1),  # Top-center
                QtCore.QPointF((x1 + x2) / 2, y2),  # Bottom-center
                QtCore.QPointF(x1, (y1 + y2) / 2),  # Left-center
                QtCore.QPointF(x2, (y1 + y2) / 2)  # Right-center
            ]

        for point in self.control_points:
            control_item = QtWidgets.QGraphicsEllipseItem(point.x() - 3, point.y() - 3, 6, 6)  # 控制点缩小到 6x6 像素
            control_item.setBrush(pg.mkBrush('b'))  # 设置控制点颜色为蓝色
            self.addItem(control_item)
            self.control_items.append(control_item)

    def mousePressEvent(self, event):
        pos = event.pos()
        view_pos = self.mapToView(pos)
        print(f"Mouse pressed at: {view_pos}, Button: {event.button()}")  # Debug information

        if event.button() == QtCore.Qt.RightButton:
            if self.shape_item is not None and self.shape_item.contains(view_pos):
                self.showCustomContextMenu(event)
            else:
                super().mousePressEvent(event)
            return

        if self.shape_type == "polygon":
            if event.button() == QtCore.Qt.LeftButton:
                self.polygon_points.append(view_pos)
                if len(self.polygon_points) > 1:
                    if self.shape_item is not None:
                        self.removeItem(self.shape_item)
                    self.shape_item = QtWidgets.QGraphicsPolygonItem(QtGui.QPolygonF(self.polygon_points))
                    self.shape_item.setPen(pg.mkPen(color='r', width=2))
                    self.addItem(self.shape_item)
                self.updateControlPoints()
            elif event.button() == QtCore.Qt.MiddleButton:
                self.completePolygon()
            return

        if self.shape_type == "dynamic_line":
            if self.clear_previous_lines and self.temp_line:
                self.removeItem(self.temp_line)
                self.temp_line = None

            if self.start_pos is None:
                self.start_pos = view_pos
                self.temp_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(self.start_pos, self.start_pos))
                self.temp_line.setPen(pg.mkPen(color='r', width=2))
                self.addItem(self.temp_line)
                print(f"Dynamic line started at: {self.start_pos}")  # Debug information
            else:
                self.temp_line.setLine(QtCore.QLineF(self.start_pos, view_pos))
                self.start_pos = view_pos
                print(f"Dynamic line updated to: {self.start_pos}")  # Debug information
            self.updateControlPoints()
            return

        if self.shape_item is not None:
            rect = self.shape_item.rect()
            for i, point in enumerate(self.control_points):
                if (point - view_pos).manhattanLength() < 10:
                    self.start_pos = view_pos
                    self.resizing = True
                    self.dragging_control_point = i
                    self.shape_initial = rect
                    self.resize_start_pos = self.start_pos
                    event.accept()
                    return

            if rect.contains(view_pos):
                self.start_pos = view_pos
                self.dragging = True
            else:
                self.removeItem(self.shape_item)
                self.shape_item = None

        if self.shape_item is None:
            self.start_pos = self.mapToView(pos)
            if self.shape_type == "rectangle":
                self.shape_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, self.start_pos))
            elif self.shape_type == "ellipse":
                self.shape_item = QtWidgets.QGraphicsEllipseItem(QtCore.QRectF(self.start_pos, self.start_pos))
            self.shape_item.setPen(pg.mkPen(color='r', width=2))
            self.addItem(self.shape_item)
            self.updateControlPoints()

        event.accept()

    def completePolygon(self):
        if len(self.polygon_points) > 2:
            self.polygon_points.append(self.polygon_points[0])
            self.shape_item.setPolygon(QtGui.QPolygonF(self.polygon_points))
        self.updateControlPoints()
        self.polygon_points = []

    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            current_pos = self.mapToView(event.pos())
            print(f"Mouse moved to: {current_pos}")  # Debug information

            if self.shape_type == "polygon":
                if len(self.polygon_points) > 0:
                    temp_points = self.polygon_points + [current_pos]
                    if self.shape_item is not None:
                        self.removeItem(self.shape_item)
                    self.shape_item = QtWidgets.QGraphicsPolygonItem(QtGui.QPolygonF(temp_points))
                    self.shape_item.setPen(pg.mkPen(color='r', width=2))
                    self.addItem(self.shape_item)
                self.updateControlPoints()
                return

            if self.shape_type == "dynamic_line":
                if self.temp_line is not None:
                    self.temp_line.setLine(QtCore.QLineF(self.start_pos, current_pos))
                else:
                    self.temp_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(self.start_pos, current_pos))
                    self.temp_line.setPen(pg.mkPen(color='r', width=2))
                    self.addItem(self.temp_line)
                return

            if self.dragging:
                dx = current_pos.x() - self.start_pos.x()
                dy = current_pos.y() - self.start_pos.y()
                rect = self.shape_item.rect()
                rect.moveTopLeft(QtCore.QPointF(rect.left() + dx, rect.top() + dy))
                self.shape_item.setRect(rect)
                self.start_pos = current_pos
                self.updateControlPoints()
            elif self.resizing and self.dragging_control_point is not None:
                rect = self.shape_initial
                if self.dragging_control_point == 0:  # Top-left
                    rect.setTopLeft(current_pos)
                elif self.dragging_control_point == 1:  # Top-right
                    rect.setTopRight(current_pos)
                elif self.dragging_control_point == 2:  # Bottom-left
                    rect.setBottomLeft(current_pos)
                elif self.dragging_control_point == 3:  # Bottom-right
                    rect.setBottomRight(current_pos)
                elif self.dragging_control_point == 4:  # Top-center
                    rect.setTop(current_pos.y())
                elif self.dragging_control_point == 5:  # Bottom-center
                    rect.setBottom(current_pos.y())
                elif self.dragging_control_point == 6:  # Left-center
                    rect.setLeft(current_pos.x())
                elif self.dragging_control_point == 7:  # Right-center
                    rect.setRight(current_pos.x())

                self.shape_item.setRect(rect)
                self.updateControlPoints()
            else:
                rect = QtCore.QRectF(self.start_pos, current_pos).normalized()
                self.shape_item.setRect(rect)
                self.updateControlPoints()
        event.accept()

    def mouseReleaseEvent(self, event):
        self.start_pos = None
        self.dragging = False
        self.resizing = False
        self.shape_initial = None
        self.resize_start_pos = None
        self.dragging_control_point = None
        event.accept()

    def showCustomContextMenu(self, event):
        menu = QtWidgets.QMenu()
        row_properties_action = menu.addAction("ROW Properties")
        row_properties_action.triggered.connect(self.showRowPropertiesDialog)

        measure_action = menu.addAction("Measure")
        measure_action.triggered.connect(self.showMeasureDialog)

        invert_action = menu.addAction("Invert")
        invert_action.triggered.connect(self.invertImage)

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

    def showMeasureDialog(self):
        if self.image_data is None or self.shape_item is None:
            return

        if self.shape_type == "polygon":
            polygon = self.shape_item.polygon()
            bounding_rect = polygon.boundingRect()
            x1, y1 = int(bounding_rect.left()), int(bounding_rect.top())
            x2, y2 = int(bounding_rect.right()), int(bounding_rect.bottom())
        else:
            rect = self.shape_item.rect()
            x1, y1 = int(rect.left()), int(rect.top())
            x2, y2 = int(rect.right()), int(rect.bottom())

        x1, x2 = max(0, x1), min(self.image_data.shape[1], x2)
        y1, y2 = max(0, y1), min(self.image_data.shape[0], y2)

        region = self.image_data[y1:y2, x1:x2]
        area = region.size
        mean_val = np.mean(region)
        min_val = np.min(region)
        max_val = np.max(region)

        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Measure")

        layout = QtWidgets.QFormLayout()

        layout.addRow(QtWidgets.QLabel("Area:"), QtWidgets.QLabel(str(area)))
        layout.addRow(QtWidgets.QLabel("Mean:"), QtWidgets.QLabel(str(mean_val)))
        layout.addRow(QtWidgets.QLabel("Min:"), QtWidgets.QLabel(str(min_val)))
        layout.addRow(QtWidgets.QLabel("Max:"), QtWidgets.QLabel(str(max_val)))

        buttons = QtWidgets.QDialogButtonBox.Ok
        button_box = QtWidgets.QDialogButtonBox(buttons)
        button_box.accepted.connect(dialog.accept)

        layout.addRow(button_box)
        dialog.setLayout(layout)
        dialog.exec_()

    def invertImage(self):
        if self.image_data is not None:
            inverted_image = 255 - self.image_data  # 简单地取反处理，假设是灰度图像
            self.image_data = inverted_image
            self.image_item.setImage(inverted_image)


class ImageWithRect(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQtGraph Example: Image with Rectangle')
        self.view = CustomViewBox()
        self.view.setAspectLocked(True)

        self.plot_item = pg.PlotItem(viewBox=self.view)
        self.addItem(self.plot_item)

        image_path = 'boats_720x576_8bits.raw'
        image = self.load_raw_image(image_path, (576, 720))
        image = np.rot90(image, k=3)

        self.img = pg.ImageItem(image)
        self.view.setImageData(image, self.img)

        self.plot_item.addItem(self.img)

        self.resize(1600, 1200)

    def load_raw_image(self, file_path, shape):
        image = np.fromfile(file_path, dtype=np.uint8)
        image = image.reshape(shape)
        return image


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ImageWithRect()
    win.show()
    sys.exit(app.exec_())
