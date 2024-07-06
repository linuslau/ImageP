import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox, \
    QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.view = QGraphicsView(self)
        self.setCentralWidget(self.view)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.scale_factor = 1.0
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def open_image(self, file_path):
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Failed to load image")

        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        self.pixmap_item.setPixmap(QPixmap.fromImage(q_image))
        self.fit_to_window()

    def fit_to_window(self):
        self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

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


# 全局变量，保存单一的 QApplication 实例和 ImageViewer 实例
app = None
viewer = None


def menu_click():
    global app, viewer

    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "Image Files (*.jpg *.jpeg *.png *.bmp)",
                                               options=options)

    if file_path:
        try:
            if not app:
                app = QApplication(sys.argv)
            if not viewer:
                viewer = ImageViewer()

            viewer.open_image(file_path)
            viewer.show()
            app.exec_()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to open image: {str(e)}")
    else:
        QMessageBox.warning(None, "No File Selected", "No image file selected.")
