import cv2
from PyQt5.QtWidgets import QFileDialog, QMessageBox

#def menu_click():
#    print("Open.py executed")

def handle_click():
    print("Open file clicked")
    # 创建文件对话框以选择图像文件
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "Image Files (*.jpg *.jpeg *.png *.bmp)", options=options)

    if file_path:
        try:
            # 使用 OpenCV 打开并显示图像
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Failed to load image")

            # 缩小图像至 25%
            scale_percent = 25
            width = int(image.shape[1] * scale_percent / 100)
            height = int(image.shape[0] * scale_percent / 100)
            dim = (width, height)
            resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

            cv2.imshow('Image Viewer', resized_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to open image: {str(e)}")
    else:
        QMessageBox.warning(None, "No File Selected", "No image file selected.")
