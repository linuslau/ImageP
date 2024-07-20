import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QLabel, QMessageBox, QInputDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
import numpy as np

class ImageJClone(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "ImageJ Clone"
        self.top = 100
        self.left = 100
        self.width = 800
        self.height = 600

        self.image_path = None
        self.original_image = None
        self.display_image = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.create_menu()

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.image_label)

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

        edit_menu = main_menu.addMenu('Edit')
        rotate_action = QAction('Rotate', self)
        rotate_action.triggered.connect(self.rotate_image)
        resize_action = QAction('Resize', self)
        resize_action.triggered.connect(self.resize_image)
        blur_action = QAction('Blur', self)
        blur_action.triggered.connect(self.blur_image)
        edge_action = QAction('Edge Detection', self)
        edge_action.triggered.connect(self.edge_detection)
        edit_menu.addAction(rotate_action)
        edit_menu.addAction(resize_action)
        edit_menu.addAction(blur_action)
        edit_menu.addAction(edge_action)

        help_menu = main_menu.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.bmp)')
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            self.display_image = self.original_image.copy()
            self.show_image(self.display_image)

    def save_image(self):
        if self.display_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Image Files (*.png *.jpg *.bmp)')
            if file_path:
                cv2.imwrite(file_path, self.display_image)
        else:
            QMessageBox.warning(self, 'Error', 'No image to save')

    def show_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def rotate_image(self):
        if self.display_image is not None:
            angle, ok = QInputDialog.getInt(self, "Rotate", "Enter angle:", 90, -360, 360, 1)
            if ok:
                (h, w) = self.display_image.shape[:2]
                center = (w // 2, h // 2)
                matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                self.display_image = cv2.warpAffine(self.display_image, matrix, (w, h))
                self.show_image(self.display_image)
        else:
            QMessageBox.warning(self, 'Error', 'No image to rotate')

    def resize_image(self):
        if self.display_image is not None:
            width, ok = QInputDialog.getInt(self, "Resize", "Enter width:", 200, 1, 10000, 1)
            if ok:
                height, ok = QInputDialog.getInt(self, "Resize", "Enter height:", 200, 1, 10000, 1)
                if ok:
                    self.display_image = cv2.resize(self.display_image, (width, height))
                    self.show_image(self.display_image)
        else:
            QMessageBox.warning(self, 'Error', 'No image to resize')

    def blur_image(self):
        if self.display_image is not None:
            ksize, ok = QInputDialog.getInt(self, "Blur", "Enter kernel size (odd number):", 5, 1, 51, 2)
            if ok:
                if ksize % 2 == 1:  # Kernel size must be odd
                    self.display_image = cv2.GaussianBlur(self.display_image, (ksize, ksize), 0)
                    self.show_image(self.display_image)
                else:
                    QMessageBox.warning(self, 'Error', 'Kernel size must be an odd number')
        else:
            QMessageBox.warning(self, 'Error', 'No image to blur')

    def edge_detection(self):
        if self.display_image is not None:
            self.display_image = cv2.Canny(self.display_image, 100, 200)
            self.show_image(self.display_image)
        else:
            QMessageBox.warning(self, 'Error', 'No image for edge detection')

    def show_about(self):
        QMessageBox.information(self, 'About', 'ImageJ Clone\nCreated with Python and PyQt')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageJClone()
    window.show()
    sys.exit(app.exec_())
