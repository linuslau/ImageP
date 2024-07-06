from PyQt5.QtWidgets import QFileDialog, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap

def menu_click():
    # 创建一个QFileDialog来选择图片
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
    if file_name:
        # 创建一个新的窗口来显示图片
        window = QWidget()
        window.setWindowTitle('Image Viewer')
        layout = QVBoxLayout()
        window.setLayout(layout)

        # 加载并显示图片
        label = QLabel()
        pixmap = QPixmap(file_name)
        label.setPixmap(pixmap)
        layout.addWidget(label)

        window.show()
        return window
