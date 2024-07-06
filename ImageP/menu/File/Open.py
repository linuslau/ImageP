# File/open.py
from PyQt5.QtWidgets import QFileDialog, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap

def handle_click():
    print("Open file clicked")

    class ImageWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.label = QLabel(self)
            self.setCentralWidget(self.label)
            self.show_image()

        def show_image(self):
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg);;All Files (*)", options=options)
            if file_name:
                pixmap = QPixmap(file_name)
                self.label.setPixmap(pixmap.scaled(self.label.size(), aspectRatioMode=1))

    window = ImageWindow()
    window.show()

