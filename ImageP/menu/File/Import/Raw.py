import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QTimer
from TestOpenCV.testPYQTG import create_and_show_image_with_rect

def handle_click():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # 打开文件选择对话框，并限制文件类型为 .raw
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Select a .raw file", "", "RAW Files (*.raw)", options=options)

    if file_path:  # 如果选择了文件
        print(f"Selected file: {file_path}")

        # 延迟加载图像，确保所有UI组件在正确的状态下被访问
        QTimer.singleShot(0, lambda: create_and_show_image_with_rect(file_path))

if __name__ == "__main__":
    handle_click()
