from PyQt5 import QtWidgets
from ui.main_ui_qt5 import Ui_MainWindow
from utils.menu_populate import populate_menu
import sys
import os


def load_menu_order(menu_path):
    order_file = os.path.join(menu_path, 'order.txt')
    if not os.path.exists(order_file):
        return []
    with open(order_file, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def add_menu_item(menu, path, is_folder):
    if is_folder:
        sub_menu = menu.addMenu(os.path.basename(path))
        populate_menu(sub_menu, path)
    else:
        action = menu.addAction(os.path.basename(path).replace('.py', ''))
        action.triggered.connect(lambda: handle_menu_click(path))


def handle_menu_click(file_path):
    # 根据文件路径导入相应模块并调用预定义的函数
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    module_spec = __import__('menu.' + module_name, fromlist=[module_name])
    if hasattr(module_spec, 'menu_click'):
        module_spec.menu_click()


def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # 获取当前脚本文件所在目录的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 定位到安装路径中的 menu 目录
    root_menu_path = os.path.join(script_dir, 'menu')

    # 如果路径不存在，尝试从包安装目录查找
    if not os.path.exists(root_menu_path):
        root_menu_path = os.path.join(os.path.dirname(__file__), 'menu')

    print(f"Root menu path: {root_menu_path}")

    if os.path.exists(root_menu_path) and os.path.isdir(root_menu_path):
        # 获取所有文件夹
        folders = [folder for folder in os.listdir(root_menu_path) if
                   os.path.isdir(os.path.join(root_menu_path, folder))]

        for folder in sorted(folders):
            folder_path = os.path.join(root_menu_path, folder)
            root_menu = ui.menubar.addMenu(folder)
            populate_menu(root_menu, folder_path)

    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
