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


def add_menu_item(menu, path, is_folder, status_bar):
    if is_folder:
        sub_menu = menu.addMenu(os.path.basename(path))
        populate_menu(sub_menu, path, status_bar)
    else:
        action = menu.addAction(os.path.basename(path).replace('.py', ''))
        action.triggered.connect(lambda: handle_menu_click(path, status_bar))
        action.hovered.connect(lambda: status_bar.showMessage(f'Hovering over {os.path.basename(path)}'))


def handle_menu_click(file_path, status_bar):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    try:
        module_spec = __import__(f'menu.{module_name}', fromlist=[module_name])
        if hasattr(module_spec, 'menu_click'):
            window = module_spec.menu_click()
            if window:
                window.setWindowTitle("ImageP")
                window.show()
    except ModuleNotFoundError as e:
        status_bar.showMessage(f"Module not found: {e}")
    except Exception as e:
        status_bar.showMessage(f"Error while handling menu click: {e}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # 获取当前脚本文件所在目录的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_menu_path = os.path.join(script_dir, 'menu')

    if not os.path.exists(root_menu_path):
        root_menu_path = os.path.join(os.path.dirname(__file__), 'menu')

    print(f"Root menu path: {root_menu_path}")

    status_bar = QtWidgets.QStatusBar()
    MainWindow.setStatusBar(status_bar)

    # 默认显示欢迎信息
    status_bar.showMessage("Welcome to use ImageP")

    if os.path.exists(root_menu_path) and os.path.isdir(root_menu_path):
        items = os.listdir(root_menu_path)
        for item in sorted(items):
            item_path = os.path.join(root_menu_path, item)
            if (os.path.isdir(item_path) and item != '__pycache__') or (item.endswith('.py') and item != '__init__.py'):
                add_menu_item(ui.menubar, item_path, os.path.isdir(item_path), status_bar)

    MainWindow.setWindowTitle("ImageP")
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
