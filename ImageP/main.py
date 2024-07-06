from PyQt5 import QtWidgets, QtCore
from ui.main_ui_qt5 import Ui_MainWindow
from utils.menu_populate import populate_menu, populate_icons
import sys
import os

def load_menu_order(menu_path):
    order_file = os.path.join(menu_path, 'order.txt')
    if not os.path.exists(order_file):
        return []
    with open(order_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def add_menu_item(menu, path, is_folder, status_bar):
    if is_folder:
        sub_menu = menu.addMenu(os.path.basename(path))
        populate_menu(sub_menu, path, status_bar)
    else:
        action = menu.addAction(os.path.basename(path).replace('.py', ''))
        action.triggered.connect(lambda: handle_menu_click(path))
        action.hovered.connect(lambda: status_bar.showMessage(os.path.basename(path).replace('.py', '')))
        menu.addAction(action)

def handle_menu_click(file_path):
    # 根据文件路径导入相应模块并调用预定义的函数
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    module_spec = __import__('menu.' + module_name, fromlist=[module_name])
    if hasattr(module_spec, 'menu_click'):
        window = module_spec.menu_click()
        if window:
            window.show()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()

    def initUI(self):
        # 获取当前脚本文件所在目录的路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 定位到安装路径中的 menu 目录
        root_menu_path = os.path.join(script_dir, 'menu')

        # Getting the root icons path
        icons_path = os.path.join(os.path.dirname(__file__), 'icons')
        print(f"Root icons path: {icons_path}")

        # 如果路径不存在，尝试从包安装目录查找
        if not os.path.exists(root_menu_path):
            root_menu_path = os.path.join(os.path.dirname(__file__), 'menu')

        print(f"Root menu path: {root_menu_path}")

        if os.path.exists(root_menu_path) and os.path.isdir(root_menu_path):
            # 获取所有文件夹和文件
            items = os.listdir(root_menu_path)

            for item in sorted(items):
                item_path = os.path.join(root_menu_path, item)
                if (os.path.isdir(item_path) and item != '__pycache__') or (item.endswith('.py') and item != '__init__.py'):
                    add_menu_item(self.ui.menubar, item_path, os.path.isdir(item_path), self.ui.statusbar)

        # Check if the icons directory exists
        if os.path.exists(icons_path) and os.path.isdir(icons_path):
            populate_icons(self.ui.toolBar, icons_path, self.ui.statusbar)

        self.ui.statusbar.showMessage("Welcome to use ImageP")

    def leaveEvent(self, event):
        self.ui.statusbar.showMessage("Welcome to use ImageP")
        super().leaveEvent(event)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.HoverEnter and isinstance(source, QtWidgets.QAction):
            self.ui.statusbar.showMessage(source.text())
        return super().eventFilter(source, event)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle("ImageP")
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
