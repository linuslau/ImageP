"""
Demonstrates common image analysis tools.

Many of the features demonstrated here are already provided by the ImageView
widget, but here we present a lower-level approach that provides finer control
over the user interface.
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PIL import Image

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

class CustomROI(pg.ROI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 添加四个边上的控制点
        self.addScaleHandle([0.5, 0], [0.5, 0.5])  # Bottom edge
        self.addScaleHandle([0.5, 1], [0.5, 0.5])  # Top edge
        self.addScaleHandle([0, 0.5], [0.5, 0.5])  # Left edge
        self.addScaleHandle([1, 0.5], [0.5, 0.5])  # Right edge

        # 添加四个顶点的虚拟控制点
        self.addScaleHandle([0, 0], [0, 0])  # Bottom-left corner
        self.addScaleHandle([0, 1], [0, 1])  # Top-left corner
        self.addScaleHandle([1, 0], [1, 0])  # Bottom-right corner
        self.addScaleHandle([1, 1], [1, 1])  # Top-right corner

        # 设置四条边的颜色为红色
        self.setPen('r')

    def contextMenuEvent(self, event):
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
        if self.item is None:
            return

        bounds = self.parentBounds()
        x1, y1 = int(bounds.left()), int(bounds.top())
        x2, y2 = int(bounds.right()), int(bounds.bottom())

        x1, x2 = max(0, x1), min(self.image_data.shape[1], x2)
        y1, y2 = max(0, y1), min(self.image_data.shape[0], y2)

        region = self.image_data[y1:y2, x1:x2]
        if region.size == 0:
            QtWidgets.QMessageBox.warning(None, "Measure", "Selected region is empty.")
            return

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

        # Add plot area to the dialog
        plot_widget = pg.PlotWidget()
        layout.addRow(plot_widget)
        plot_widget.plot(region.mean(axis=0), pen='b')

        buttons = QtWidgets.QDialogButtonBox.Ok
        button_box = QtWidgets.QDialogButtonBox(buttons)
        button_box.accepted.connect(dialog.accept)

        layout.addRow(button_box)
        dialog.setLayout(layout)
        dialog.exec_()

    def invertImage(self):
        if self.item is not None:
            inverted_image = 255 - self.image_data  # 简单地取反处理，假设是灰度图像
            self.image_data = inverted_image
            self.item.setImage(inverted_image)


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
        self.image_data = None
        self.image_item = None
        self.handles = []

    def setImageData(self, image_data, image_item):
        self.image_data = image_data
        self.image_item = image_item

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
                self.clearOldRect()
                self.start_pos = self.mapToView(pos)
                self.rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, self.start_pos))
                self.rect_item.setPen(pg.mkPen(color='r', width=2))
                self.addItem(self.rect_item)
                self.createHandles(self.rect_item)
        else:
            self.start_pos = self.mapToView(pos)
            self.rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, self.start_pos))
            self.rect_item.setPen(pg.mkPen(color='r', width=2))
            self.addItem(self.rect_item)
            self.createHandles(self.rect_item)

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
            self.updateHandles(self.rect_item)
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
        if self.image_data is None or self.rect_item is None:
            return

        rect = self.rect_item.rect()
        x1, y1 = int(rect.left()), int(rect.top())
        x2, y2 = int(rect.right()), int(rect.bottom())

        x1, x2 = max(0, x1), min(self.image_data.shape[1], x2)
        y1, y2 = max(0, y1), min(self.image_data.shape[0], y2)

        region = self.image_data[y1:y2, x1:x2]
        if region.size == 0:
            QtWidgets.QMessageBox.warning(None, "Measure", "Selected region is empty.")
            return

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

        # Add plot area to the dialog
        plot_widget = pg.PlotWidget()
        layout.addRow(plot_widget)
        plot_widget.plot(region.mean(axis=0), pen='b')

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

    def createHandles(self, rect_item):
        """Create handles at the corners and edges of the rectangle."""
        self.handles = []
        rect = rect_item.rect()
        handle_positions = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight(),
            rect.topLeft() + QtCore.QPointF(rect.width()/2, 0),
            rect.topRight() + QtCore.QPointF(0, rect.height()/2),
            rect.bottomLeft() + QtCore.QPointF(rect.width()/2, 0),
            rect.bottomRight() + QtCore.QPointF(-rect.width()/2, 0)
        ]

        for pos in handle_positions:
            handle = QtWidgets.QGraphicsEllipseItem(-3, -3, 6, 6)
            handle.setPen(pg.mkPen(None))
            handle.setBrush(pg.mkBrush('b'))
            handle.setPos(pos)
            self.handles.append(handle)
            self.addItem(handle)

    def updateHandles(self, rect_item):
        """Update handle positions when the rectangle is resized or moved."""
        rect = rect_item.rect()
        handle_positions = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight(),
            rect.topLeft() + QtCore.QPointF(rect.width()/2, 0),
            rect.topRight() + QtCore.QPointF(0, rect.height()/2),
            rect.bottomLeft() + QtCore.QPointF(rect.width()/2, 0),
            rect.bottomRight() + QtCore.QPointF(-rect.width()/2, 0)
        ]

        for handle, pos in zip(self.handles, handle_positions):
            handle.setPos(pos)

    def clearOldRect(self):
        """Remove the old rectangle and its handles."""
        if self.rect_item is not None:
            self.removeItem(self.rect_item)
            self.rect_item = None
        for handle in self.handles:
            self.removeItem(handle)
        self.handles = []

class ImageWithRect(pg.GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('pyqtgraph example: Image Analysis')
        self.view = CustomViewBox()
        self.view.setAspectLocked(True)

        # 在窗口中添加一个图像视图
        self.plot_item = pg.PlotItem(viewBox=self.view)
        self.addItem(self.plot_item)

        # 读取并显示指定图像
        image_path = 'boats.jpg'  # 替换为你的图像路径
        image = Image.open(image_path)
        data = np.array(image)

        # 翻转图像数据
        data = np.flipud(data)

        self.img = pg.ImageItem(data)
        self.view.setImageData(data, self.img)  # 设置图像数据，以便进行测量

        self.plot_item.addItem(self.img)

        # 设置窗口初始大小
        self.resize(1600, 1200)

        # 自定义 ROI 和直方图
        self.setupROIAndHistogram()

    def setupROIAndHistogram(self):
        # Custom ROI for selecting an image region
        roi = CustomROI([-8, 14], [6, 5])
        self.view.addItem(roi)
        roi.setZValue(10)  # make sure ROI is drawn above image

        # Isocurve drawing
        iso = pg.IsocurveItem(level=0.8, pen='g')
        iso.setParentItem(self.img)
        iso.setZValue(5)

        # Contrast/color control
        hist = pg.HistogramLUTItem()
        hist.setImageItem(self.img)
        hist.setMinimumWidth(250)  # 设置最小宽度
        self.addItem(hist)

        # Draggable line for setting isocurve level
        isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
        hist.vb.addItem(isoLine)
        hist.vb.setMouseEnabled(y=False) # makes user interaction a little easier
        isoLine.setValue(0.8)
        isoLine.setZValue(1000) # bring iso line above contrast controls

        # Another plot area for displaying ROI data
        self.nextRow()
        #p2 = self.addPlot(colspan=2)
        #p2.setMaximumHeight(250)

        # Callbacks for handling user interaction
        def updatePlot():
            selected = roi.getArrayRegion(self.img.image, self.img)
            #p2.plot(selected.mean(axis=0), clear=True)

        roi.sigRegionChanged.connect(updatePlot)
        updatePlot()

        def updateIsocurve():
            iso.setLevel(isoLine.value())

        isoLine.sigDragged.connect(updateIsocurve)

        def imageHoverEvent(event):
            """Show the position, pixel, and value under the mouse cursor."""
            if event.isExit():
                self.plot_item.setTitle("")
                return
            pos = event.pos()
            i, j = pos.y(), pos.x()
            i = int(np.clip(i, 0, self.img.image.shape[0] - 1))
            j = int(np.clip(j, 0, self.img.image.shape[1] - 1))
            val = self.img.image[i, j]
            ppos = self.img.mapToParent(pos)
            x, y = ppos.x(), ppos.y()
            self.plot_item.setTitle("pos: (%0.1f, %0.1f)  pixel: (%d, %d)  value: %.3g" % (x, y, i, j, val))

        # Monkey-patch the image to use our custom hover function.
        # This is generally discouraged (you should subclass ImageItem instead),
        # but it works for a very simple use like this.
        self.img.hoverEvent = imageHoverEvent

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
