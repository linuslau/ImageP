import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QSlider, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
import os  # Import os to work with file paths
from ImageP.utils.state_manager import state_manager
import subprocess


class CustomEllipseItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.setRect(-5, -5, 10, 10)  # Ensure consistent size for all control points

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawEllipse(self.rect())  # Use the set rectangle for drawing

class CustomSlider(QSlider):
    def wheelEvent(self, event):
        # Do not call the parent class's wheelEvent, as it defaults to +3
        # super().wheelEvent(event)

        # Custom layer switching logic
        delta = event.angleDelta().y()
        current_value = self.value()

        # Adjust the layer count based on the scroll direction, increasing or decreasing by one layer at a time
        if delta > 0 and current_value < self.maximum():
            self.setValue(current_value + 1)
        elif delta < 0 and current_value > 0:
            self.setValue(current_value - 1)

        # Update the label
        self.parent().update_label_text(self.value())
        event.accept()

class CustomViewBox(pg.ViewBox):
    # Your existing CustomViewBox class implementation
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
        self.shape_type = "rectangle"  # "rectangle", "ellipse", "polygon", "dynamic_line", "dynamic_polygon"
        self.last_shape_type = self.shape_type
        self.polygon_points = []
        self.temp_line = None
        self.dynamic_lines = []
        self.clear_previous_lines = False  # Flag to control whether to clear previous lines
        self.temp_dynamic_line = None
        self.current_index = -1
        self.moved = False  # Track if the mouse has moved
        self.dragging_line = False

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

        if self.shape_type in ["polygon", "dynamic_polygon"]:
            self.control_points = self.polygon_points
        elif self.shape_type == "dynamic_line":
            line = self.shape_item.line()
            p1 = line.p1()
            p2 = line.p2()
            self.control_points = [
                p1,
                p2,
                QtCore.QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            ]
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
            control_item = CustomEllipseItem()
            control_item.setBrush(pg.mkBrush('w'))  # Keep the control point color white
            control_item.setPos(point)  # Use the setPos method to position the control point correctly
            self.addItem(control_item)
            self.control_items.append(control_item)

    def clear_lines(self):
        """清除所有绘制的线条"""
        if self.shape_type == 'dynamic_line' or self.last_shape_type == 'dynamic_line':
            items = self.allChildItems()
            for item in items:
                if isinstance(item, QtWidgets.QGraphicsLineItem) or isinstance(item, QtWidgets.QGraphicsEllipseItem):
                    self.removeItem(item)
        else:
            for item in self.dynamic_lines:
                self.removeItem(item)

        self.dynamic_lines.clear()
        self.polygon_points.clear()
        if self.shape_item:
            self.removeItem(self.shape_item)
            self.shape_item = None
        self.updateControlPoints()

    def mousePressEvent(self, event):
        pos = event.pos()
        view_pos = self.mapToView(pos)
        self.moved = False  # Reset moved flag
        print(f"Mouse pressed at: {view_pos}, Button: {event.button()}")  # Debug information

        if event.button() == QtCore.Qt.RightButton:
            if self.shape_item is not None and self.shape_item.contains(view_pos):
                self.showCustomContextMenu(event)
            else:
                super().mousePressEvent(event)
            return

        # Clear the previous control points when starting a new drawing or upon clicking
        if self.shape_type in ["rectangle", "ellipse"] and self.shape_item is not None:
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
                # Start dragging the existing shape instead of clearing it
                self.start_pos = view_pos
                self.dragging = True
                event.accept()
                return
            self.clear_lines()

        # Check if near a control point in dynamic_line mode
        near_control_point = False
        if self.shape_type == "dynamic_line":
            for point in self.control_points:
                if (point - view_pos).manhattanLength() < 10:
                    near_control_point = True
                    break

        if self.clear_previous_lines and not near_control_point:
            self.clear_lines()

        if self.shape_type == "polygon":
            if event.button() == QtCore.Qt.LeftButton:
                self.polygon_points.append(view_pos)
                control_item = CustomEllipseItem()
                control_item.setBrush(pg.mkBrush('w'))
                control_item.setPos(view_pos)  # Use the setPos method to position the control point correctly
                self.addItem(control_item)
                self.control_items.append(control_item)
                if len(self.polygon_points) > 1:
                    if self.shape_item is not None:
                        self.removeItem(self.shape_item)
                    self.shape_item = QtWidgets.QGraphicsPolygonItem(QtGui.QPolygonF(self.polygon_points))
                    self.shape_item.setPen(pg.mkPen(color='r', width=2))
                    self.addItem(self.shape_item)
            elif event.button() == QtCore.Qt.MiddleButton:
                self.completePolygon()
            return

        if self.shape_type == "dynamic_line":
            for i, point in enumerate(self.control_points):
                if (point - view_pos).manhattanLength() < 10:
                    self.dragging_control_point = i
                    self.start_pos = view_pos
                    if i == 2:
                        self.dragging_line = True
                    event.accept()
                    return

            if self.start_pos is None:
                # First click: store the start position, but don't create any item yet
                self.start_pos = view_pos
                print(f"Dynamic line started at: {self.start_pos}")  # Debug information
                event.accept()
                return

            if not self.dragging_line:
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

        if self.shape_type == "dynamic_polygon":
            if event.button() == QtCore.Qt.LeftButton:
                mouse_point = view_pos
                new_point = (mouse_point.x(), mouse_point.y())
                print(f"Clicked point: {new_point}")

                if self.start_pos is None:
                    self.start_pos = new_point
                    self.initial_point = self.start_pos
                    control_item = CustomEllipseItem()
                    control_item.setBrush(pg.mkBrush('r'))
                    control_item.setPos(QtCore.QPointF(*self.start_pos))
                    self.addItem(control_item)
                    self.control_items.append(control_item)
                    print(f"Initial point set: {self.initial_point}")
                else:
                    # For subsequent points, finalize the previous line and prepare for the next
                    if self.temp_line:
                        self.removeItem(self.temp_line)
                        self.temp_line = None

                    # Add the finalized line
                    line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(QtCore.QPointF(*self.start_pos), mouse_point))
                    line.setPen(pg.mkPen(color='r', width=2))
                    self.addItem(line)
                    self.dynamic_lines.append(line)

                    # Ensure that the next round of drawing does not affect the previous round's last line
                    if self.is_close_to_initial_point(new_point):
                        control_item = CustomEllipseItem()
                        control_item.setBrush(pg.mkBrush('w'))
                        control_item.setPos(QtCore.QPointF(*self.start_pos))
                        self.addItem(control_item)
                        self.control_items.append(control_item)
                        self.end_current_round()
                        print("Ending current round")
                        return
                    else:
                        self.start_pos = new_point
                        control_item = CustomEllipseItem()
                        control_item.setBrush(pg.mkBrush('w'))
                        control_item.setPos(QtCore.QPointF(*self.start_pos))
                        self.addItem(control_item)
                        self.control_items.append(control_item)
                        print(f"New line drawn to: {new_point}")
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
            if self.shape_type not in ["rectangle", "ellipse"]:
                self.updateControlPoints()

        event.accept()

    def completePolygon(self):
        if len(self.polygon_points) > 2:
            self.polygon_points.append(self.polygon_points[0])
            self.shape_item.setPolygon(QtGui.QPolygonF(self.polygon_points))
        self.updateControlPoints()
        self.polygon_points = []

    def on_mouse_move(self, pos):
        scene_pos = pos  # Get the position in the scene coordinates
        current_pos = self.mapSceneToView(scene_pos)  # Convert scene coordinates to view coordinates
        # print("on_mouse_move")
        if self.shape_type == "dynamic_polygon" and self.start_pos is not None:
            print(f"Mouse moved to: {current_pos}")  # Debug information

            # Remove the last temporary line if it exists
            if self.temp_line:
                self.removeItem(self.temp_line)

            # Draw the current line from start_pos to the current mouse position
            self.temp_line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(QtCore.QPointF(*self.start_pos), current_pos))
            self.temp_line.setPen(pg.mkPen(color='r', width=2))
            self.addItem(self.temp_line)

    def mouseMoveEvent(self, event):
        self.moved = True  # Set moved flag to True when mouse is moved
        print("mouseMoveEvent--------------------")
        if self.start_pos is not None and self.shape_type != "dynamic_polygon":
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
                if self.dragging_control_point is not None:
                    line = self.shape_item.line()
                    if self.dragging_control_point == 0:
                        line.setP1(current_pos)
                    elif self.dragging_control_point == 1:
                        line.setP2(current_pos)
                    elif self.dragging_control_point == 2:
                        dx = current_pos.x() - self.start_pos.x()
                        dy = current_pos.y() - self.start_pos.y()
                        line.translate(dx, dy)
                        self.start_pos = current_pos
                    self.shape_item.setLine(line)
                    self.updateControlPoints()
                else:
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
        if self.shape_type == "dynamic_line":
            if self.temp_line is not None:
                self.shape_item = self.temp_line
                self.temp_line = None
            self.updateControlPoints()
            self.start_pos = None
            self.dragging_control_point = None
            self.dragging_line = False
        if self.shape_type in ["rectangle", "ellipse"]:
            if not self.moved:
                if self.shape_item is not None:
                    self.removeItem(self.shape_item)
                    self.shape_item = None
            self.updateControlPoints()
            self.start_pos = None
            self.dragging = False
            self.resizing = False
            self.shape_initial = None
            self.resize_start_pos = None
            self.dragging_control_point = None
        event.accept()

    def is_close_to_initial_point(self, point, threshold=5):
        """判断当前点是否接近初始点"""
        distance = ((point[0] - self.initial_point[0]) ** 2 + (point[1] - self.initial_point[1]) ** 2) ** 0.5
        print(f"Distance from initial point: {distance}")
        return distance < threshold

    def end_current_round(self):
        """结束当前轮绘制"""
        self.start_pos = None
        self.temp_line = None
        self.initial_point = None
        if self.clear_previous_lines:
            for item in self.dynamic_lines:
                self.removeItem(item)
            self.dynamic_lines.clear()

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


class ImageWithRect(QWidget):
    def __init__(self):
        super().__init__()

        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.graphics_widget)

        self.view = CustomViewBox()
        self.view.setAspectLocked(True)

        self.plot_item = pg.PlotItem(viewBox=self.view)
        self.graphics_widget.addItem(self.plot_item)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.label.setStyleSheet("background-color: black; color: white;")

        self.layout.addWidget(self.label)

        self.image_path = 'boats_720x576_8bits.raw'
        image = self.load_raw_image(self.image_path, (576, 720))
        image = np.rot90(image, k=3)

        self.img = pg.ImageItem(image)
        self.view.setImageData(image, self.img)

        self.plot_item.addItem(self.img)

        self.setWindowTitle(os.path.basename(self.image_path))  # Set window title to file name

        # Add histogram LUT item for the right-side panel
        self.histogram_lut = pg.HistogramLUTItem()
        self.histogram_lut.setImageItem(self.img)
        self.graphics_widget.addItem(self.histogram_lut)

        self.slider = None
        self.is_3d = False
        self.is_playing = False  # Track the play/pause state
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_layer)

        self.setup_ui()

        self.resize(1600, 1200)

        # Connect mouse move signal
        self.plot_item.scene().sigMouseMoved.connect(self.on_mouse_move)
    def render_3d_image(self):
        # Replace with the actual filename or make it dynamic
        file_name = 'maotai_384x384x384.raw'
        subprocess.run(['python', '../TestOpenCV/test3DRender.py', file_name])
    def setup_ui(self):
        # Create custom slider
        self.slider = CustomSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.update_image_layer)

        # Create buttons
        self.prev_button = QPushButton("◀")
        self.prev_button.setFixedSize(40, 40)
        self.next_button = QPushButton("▶")
        self.next_button.setFixedSize(40, 40)
        self.play_button = QPushButton("⯈")  # Play button
        self.play_button.setFixedSize(40, 40)

        # Connect buttons to methods
        self.prev_button.clicked.connect(self.decrease_layer)
        self.next_button.clicked.connect(self.increase_layer)
        self.play_button.clicked.connect(self.toggle_play_pause)

        # Arrange buttons and slider in a horizontal layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.play_button)
        hbox.addWidget(self.prev_button)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.next_button)

        # Add to the main layout
        self.layout.addLayout(hbox)

        self.render_button = QPushButton("Render 3D")
        #self.render_button.setFixedSize(100, 40)
        self.render_button.adjustSize()
        self.render_button.clicked.connect(self.render_3d_image)

        # Add the button to your layout
        hbox.addWidget(self.render_button)

    def load_raw_image(self, file_path, shape, dtype=np.uint8):
        image = np.fromfile(file_path, dtype=dtype)
        image = image.reshape(shape)
        return image

    def load_3d_image(self, file_path, shape, dtype=np.float32):
        image = np.fromfile(file_path, dtype=dtype)
        image = image.byteswap().newbyteorder()  # Handle little-endian data
        image = image.reshape(shape)
        return image

    def display_3d_image(self, file_path, shape):
        self.image_data = self.load_3d_image(file_path, shape)
        self.is_3d = True

        # Initialize first layer
        image_layer = self.image_data[0, :, :]
        self.img.setImage(image_layer)

        # Set slider range
        self.slider.setRange(0, shape[0] - 1)

        # Update label with initial layer
        self.update_label_text(0)

    def update_image_layer(self, value):
        if self.is_3d:
            image_layer = self.image_data[value, :, :]
            self.img.setImage(image_layer)
            self.update_label_text(value)

    def update_label_text(self, layer):
        """Update the label with layer information."""
        if self.is_3d and self.slider:
            total_layers = self.image_data.shape[0]
            i, j = 0, 0  # assuming the top-left pixel for this example
            val = self.image_data[layer, i, j]
            self.label.setText(f"pos: ({j:.1f}, {i:.1f})  pixel: ({i}, {j})  layer: {layer + 1}/{total_layers}  value: {val:.4f}")

    def on_mouse_move(self, pos):
        self.view.on_mouse_move(pos)
        self.update_label(pos)

    def update_label(self, pos):
        pos = self.view.mapSceneToView(pos)
        i, j = int(pos.y()), int(pos.x())
        if self.is_3d and self.slider:
            layer = self.slider.value()
            i = np.clip(i, 0, self.image_data.shape[1] - 1)
            j = np.clip(j, 0, self.image_data.shape[2] - 1)
            val = self.image_data[layer, i, j]
            total_layers = self.image_data.shape[0]
            self.label.setText(f"pos: ({pos.x():.1f}, {pos.y():.1f})  pixel: ({i}, {j})  layer: {layer + 1}/{total_layers}  value: {val:.4f}")
        else:
            i = np.clip(i, 0, self.view.image_data.shape[0] - 1)
            j = np.clip(j, 0, self.view.image_data.shape[1] - 1)
            val = self.view.image_data[i, j]
            self.label.setText(f"pos: ({pos.x():.1f}, {pos.y():.1f})  pixel: ({i}, {j})  value: {val:.4f}")

    def wheelEvent(self, event):
        if self.is_3d and self.slider:
            delta = event.angleDelta().y()
            current_value = self.slider.value()
            if delta > 0 and current_value < self.slider.maximum():
                self.slider.setValue(current_value + 1)
            elif delta < 0 and current_value > 0:
                self.slider.setValue(current_value - 1)
            event.accept()
        else:
            super().wheelEvent(event)

    def increase_layer(self):
        if self.is_3d and self.slider.value() < self.slider.maximum():
            self.slider.setValue(self.slider.value() + 1)

    def decrease_layer(self):
        if self.is_3d and self.slider.value() > 0:
            self.slider.setValue(self.slider.value() - 1)

    def toggle_play_pause(self):
        if self.is_playing:
            self.timer.stop()
            self.play_button.setText("⯈")  # Change to play icon
        else:
            self.timer.start(100)  # Adjust the interval as needed
            self.play_button.setText("⏸")  # Change to pause icon
        self.is_playing = not self.is_playing

    def play_next_layer(self):
        if self.slider.value() < self.slider.maximum():
            self.slider.setValue(self.slider.value() + 1)
        else:
            self.slider.setValue(0)  # Loop back to the first layer


def create_and_show_image_with_rect():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        created_app = True
    else:
        created_app = False

    image_with_rect = ImageWithRect()

    selected_shape_type = state_manager.get_shape_type()
    clear_previous_lines = state_manager.get_clear_previous_lines()
    if clear_previous_lines:
        image_with_rect.view.clear_previous_lines = True
    image_with_rect.view.shape_type = selected_shape_type
    image_with_rect.view.clear_lines()

    # Load the 3D image if required
    image_with_rect.display_3d_image('maotai_384x384x384.raw', (384, 384, 384))

    # Connect to main window signal if main window is present
    main_window = QtWidgets.QApplication.instance().activeWindow()
    if main_window:
        main_window.icon_clicked.connect(lambda index: on_icon_clicked(index, image_with_rect.view))

    image_with_rect.show()

    if created_app:
        sys.exit(app.exec_())


def on_icon_clicked(index, view):
    shape_types = ["rectangle", "ellipse", "polygon", "dynamic_polygon", "dynamic_line", "dynamic_line"]
    if 0 <= index < len(shape_types):
        if view.current_index == index:
            print(f"Shape type {shape_types[index]} already selected and remains grey.")
        else:
            # Before switching modes, clear any unfinished lines in dynamic_polygon mode
            if view.shape_type == "dynamic_polygon":
                if view.temp_line:
                    view.removeItem(view.temp_line)
                    view.temp_line = None
                if view.dynamic_lines:
                    last_line = view.dynamic_lines[-1]
                    if isinstance(last_line, QtWidgets.QGraphicsLineItem):
                        view.removeItem(last_line)
                        view.dynamic_lines.pop()

            # Switch shape type
            view.last_shape_type = view.shape_type
            view.shape_type = shape_types[index]
            view.clear_lines()  # Clear lines when switching shapes
            view.current_index = index
            view.clear_previous_lines = False
            if view.shape_type == "dynamic_polygon":
                view.start_pos = None
                view.initial_point = None
            elif view.shape_type == "dynamic_line":
                if index == 5:
                    view.clear_previous_lines = True
                else:
                    view.clear_previous_lines = False
                view.start_pos = None
                view.temp_line = None
            print(f"Shape type set to: {shape_types[index]}")



if __name__ == '__main__':
    create_and_show_image_with_rect()
