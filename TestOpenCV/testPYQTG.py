import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QPen
from PyQt5.QtCore import Qt, QRectF, QPointF
import numpy as np
import cv2

class ImageJClone(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ImageJ Clone")
        self.setGeometry(100, 100, 800, 600)

        self.image_path = None
        self.original_image = None
        self.display_image = None

        self.drawing = False
        self.start_point = QPointF()
        self.end_point = QPointF()
        self.rect_item = None
        self.rects = []

        self.initUI()

    def initUI(self):
        self.create_menu()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Create a GraphicsView and GraphicsScene
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.layout.addWidget(self.graphics_view)

        # Install event filter
        self.graphics_view.viewport().installEventFilter(self)

    def create_menu(self):
        main_menu = self.menuBar()

        file_menu = main_menu.addMenu('File')
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_image)
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_image)
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        help_menu = main_menu.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.bmp *.tif *.tiff)')
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if self.original_image is None:
                self.show_warning("Failed to load image")
                return
            self.display_image = self.original_image.copy()
            self.show_image(self.display_image)

    def save_image(self):
        if self.display_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Image Files (*.png *.jpg *.bmp *.tif *.tiff)')
            if file_path:
                cv2.imwrite(file_path, self.display_image)
        else:
            self.show_warning("No image to save")

    def show_image(self, image):
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphics_view.setScene(self.scene)
            self.redraw_rectangles()

    def redraw_rectangles(self):
        for rect in self.rects:
            rect_item = QGraphicsRectItem(QRectF(rect[0], rect[1]))
            rect_item.setPen(QPen(Qt.green, 2))
            self.scene.addItem(rect_item)

    def show_about(self):
        QMessageBox.information(self, "About", "ImageJ Clone\nCreated with Python and PyQt5")

    def show_warning(self, message):
        QMessageBox.warning(self, "Warning", message)

    def eventFilter(self, source, event):
        if source == self.graphics_view.viewport():
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                self.drawing = True
                self.start_point = self.graphics_view.mapToScene(event.pos())
                if self.rect_item:
                    self.scene.removeItem(self.rect_item)
                self.rect_item = QGraphicsRectItem(QRectF(self.start_point, self.start_point))
                self.rect_item.setPen(QPen(Qt.green, 2))
                self.scene.addItem(self.rect_item)
            elif event.type() == event.MouseMove and self.drawing:
                self.end_point = self.graphics_view.mapToScene(event.pos())
                rect = QRectF(self.start_point, self.end_point)
                self.rect_item.setRect(rect)
            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.drawing = False
                self.end_point = self.graphics_view.mapToScene(event.pos())
                rect = QRectF(self.start_point, self.end_point)
                self.rect_item.setRect(rect)
                self.rects.append((self.start_point, self.end_point))
        return super().eventFilter(source, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageJClone()
    window.show()
    sys.exit(app.exec_())
