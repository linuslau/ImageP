import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import QTimer
from TestOpenCV.testPYQTG import create_and_show_image_with_rect

CONFIG_FILE = "import_dialog_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def show_import_dialog():
    dialog = QDialog()
    dialog.setWindowTitle("Import > Raw...")

    # 设置对话框的最小宽度
    dialog.setMinimumWidth(600)

    # 加载上次保存的配置
    config = load_config()

    layout = QVBoxLayout()

    # Image type dropdown
    image_type_label = QLabel("Image type:")
    image_type_combo = QComboBox()
    image_type_combo.addItems([
        "8-bit", "16-bit Signed", "16-bit Unsigned", "32-bit Signed", "32-bit Unsigned",
        "32-bit Real", "64-bit Real", "24-bit RGB", "24-bit RGB Planar", "24-bit BGR",
        "24-bit Integer", "32-bit ARGB", "32-bit ABGR", "1-bit Bitmap"
    ])
    image_type_combo.setCurrentText(config.get('image_type', '8-bit'))
    layout.addWidget(image_type_label)
    layout.addWidget(image_type_combo)

    # Width and Height inputs
    width_label = QLabel("Width (pixels):")
    width_input = QLineEdit()
    width_input.setPlaceholderText("Enter width, can't be 0")
    width_input.setText(str(config.get('width', '')))
    height_label = QLabel("Height (pixels):")
    height_input = QLineEdit()
    height_input.setPlaceholderText("Enter height, can't be 0")
    height_input.setText(str(config.get('height', '')))
    layout.addWidget(width_label)
    layout.addWidget(width_input)
    layout.addWidget(height_label)
    layout.addWidget(height_input)

    # Offset to first image
    offset_label = QLabel("Offset to first image (bytes):")
    offset_input = QLineEdit()
    offset_input.setPlaceholderText("Enter offset, default 0")
    offset_input.setText(str(config.get('offset', '')))
    layout.addWidget(offset_label)
    layout.addWidget(offset_input)

    # Number of images
    num_images_label = QLabel("Number of images:")
    num_images_input = QLineEdit()
    num_images_input.setPlaceholderText("Enter number, default 1")
    num_images_input.setText(str(config.get('num_images', '')))
    layout.addWidget(num_images_label)
    layout.addWidget(num_images_input)

    # Gap between images
    gap_label = QLabel("Gap between images (bytes):")
    gap_input = QLineEdit()
    gap_input.setPlaceholderText("Enter gap, default 0")
    gap_input.setText(str(config.get('gap', '')))
    layout.addWidget(gap_label)
    layout.addWidget(gap_input)

    # Checkboxes
    white_zero_checkbox = QCheckBox("White is zero")
    white_zero_checkbox.setChecked(config.get('white_zero', False))
    little_endian_checkbox = QCheckBox("Little-endian byte order")
    little_endian_checkbox.setChecked(config.get('little_endian', False))
    open_all_files_checkbox = QCheckBox("Open all files in folder")
    open_all_files_checkbox.setChecked(config.get('open_all_files', False))
    virtual_stack_checkbox = QCheckBox("Use virtual stack")
    virtual_stack_checkbox.setChecked(config.get('virtual_stack', False))
    layout.addWidget(white_zero_checkbox)
    layout.addWidget(little_endian_checkbox)
    layout.addWidget(open_all_files_checkbox)
    layout.addWidget(virtual_stack_checkbox)

    # OK and Cancel buttons
    button_layout = QHBoxLayout()
    button_ok = QPushButton("OK")
    button_cancel = QPushButton("Cancel")
    button_ok.setFixedWidth(100)  # 设置按钮的宽度
    button_cancel.setFixedWidth(100)
    button_layout.addWidget(button_ok)
    button_layout.addWidget(button_cancel)
    layout.addLayout(button_layout)

    # Set layout and show dialog
    dialog.setLayout(layout)

    # Handling the button click events
    button_ok.clicked.connect(dialog.accept)
    button_cancel.clicked.connect(dialog.reject)

    if dialog.exec_() == QDialog.Accepted:
        # Capture all the selected values from the dialog
        params = {
            'image_type': image_type_combo.currentText(),
            'width': int(width_input.text()) if width_input.text().strip() != '' else 0,
            'height': int(height_input.text()) if height_input.text().strip() != '' else 0,
            'offset': int(offset_input.text()) if offset_input.text().strip() != '' else 0,
            'num_images': int(num_images_input.text()) if num_images_input.text().strip() != '' else 1,
            'gap': int(gap_input.text()) if gap_input.text().strip() != '' else 0,
            'white_zero': white_zero_checkbox.isChecked(),
            'little_endian': little_endian_checkbox.isChecked(),
            'open_all_files': open_all_files_checkbox.isChecked(),
            'virtual_stack': virtual_stack_checkbox.isChecked()
        }

        # Save the configuration to file
        save_config(params)

        return params
    else:
        return None

def handle_click():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # 打开文件选择对话框，并限制文件类型为 .raw
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(None, "Select a .raw file", "", "RAW Files (*.raw)", options=options)

    if file_path:  # 如果选择了文件
        print(f"Selected file: {file_path}")

        # 显示Import > Raw...对话框，并获取参数
        params = show_import_dialog()
        if params:  # 如果用户点击了OK并选择了参数
            # 延迟加载图像，确保所有UI组件在正确的状态下被访问
            QTimer.singleShot(0, lambda: create_and_show_image_with_rect(file_path, params))

if __name__ == "__main__":
    handle_click()
