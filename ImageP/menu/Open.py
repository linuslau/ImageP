import cv2
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox, QGraphicsPixmapItem, QApplication, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import time

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.view = QGraphicsView(self)
        self.setCentralWidget(self.view)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.pixmap_item = None  # Store the current pixmap item
        self.loading_label = QLabel("Loading image...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("QLabel { background-color : white; color : black; }")
        self.loading_label.setGeometry(0, 0, 800, 600)
        self.loading_label.setVisible(False)

        self.scale_factor = 1.0
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def open_image(self, file_path):
        self.loading_label.setVisible(True)
        self.show()

        # Clean up previous pixmap item
        if self.pixmap_item:
            self.scene.removeItem(self.pixmap_item)
            self.pixmap_item = None

        self.thread = ImageLoaderThread(file_path)
        self.thread.image_loaded.connect(self.display_image)
        self.thread.start()

    def display_image(self, q_image):
        # Create a new pixmap item
        pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(q_image))
        self.scene.addItem(pixmap_item)

        # Fit view to the new pixmap item
        pixmap_item_width = pixmap_item.boundingRect().width()
        pixmap_item_height = pixmap_item.boundingRect().height()
        self.view.setSceneRect(0, 0, pixmap_item_width, pixmap_item_height)
        self.view.fitInView(pixmap_item, Qt.KeepAspectRatio)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Hide loading label
        self.loading_label.setVisible(False)

        # Store the current pixmap item
        self.pixmap_item = pixmap_item

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale_image(1.25)
            else:
                self.scale_image(0.8)
        else:
            super().wheelEvent(event)

    def scale_image(self, factor):
        self.scale_factor *= factor
        self.view.scale(factor, factor)

class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(QImage)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        start_time = time.time()
        image = cv2.imread(self.file_path)
        if image is None:
            raise ValueError("Failed to load image")
        print(f"Image load time: {time.time() - start_time:.4f} seconds")

        start_time = time.time()
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        print(f"Image conversion time: {time.time() - start_time:.4f} seconds")

        self.image_loaded.emit(q_image)

# 全局变量，保存单一的 QApplication 实例和 ImageViewer 实例
app = None
viewer = None

def menu_click():
    global app, viewer

    start_time = time.time()
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "Image Files (*.jpg *.jpeg *.png *.bmp)", options=options)
    print(f"File dialog time: {time.time() - start_time:.4f} seconds")

    if file_path:
        try:
            step_time = time.time()
            if not app:
                app = QApplication(sys.argv)
            print(f"QApplication creation time: {time.time() - step_time:.4f} seconds")

            step_time = time.time()
            if not viewer:
                viewer = ImageViewer()
            print(f"ImageViewer creation time: {time.time() - step_time:.4f} seconds")

            step_time = time.time()
            viewer.open_image(file_path)
            print(f"Open image time: {time.time() - step_time:.4f} seconds")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to open image: {str(e)}")
    else:
        QMessageBox.warning(None, "No File Selected", "No image file selected.")
