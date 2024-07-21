import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QLabel, QMessageBox, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
import pyqtgraph as pg
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

        self.initUI()

    def initUI(self):
        self.create_menu()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Create a GraphicsView
        self.graphics_view = pg.GraphicsView()
        self.layout.addWidget(self.graphics_view)

        # Create a ViewBox
        self.view_box = pg.ViewBox()
        self.graphics_view.setCentralItem(self.view_box)

        # Create an ImageItem
        self.image_item = pg.ImageItem()
        self.view_box.addItem(self.image_item)

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
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            else:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.image_item.setImage(np.rot90(image, 3), levels=(0, 255))
            self.view_box.autoRange()

    def show_about(self):
        self.show_message("About", "ImageJ Clone\nCreated with Python and PyQtGraph")

    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageJClone()
    window.show()
    sys.exit(app.exec_())
