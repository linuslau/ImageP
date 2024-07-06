from main_ui_qt5 import *
import sys
import os
import importlib.util
from PyQt5 import QtWidgets

def load_and_bind_action(action, module_path):
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, 'handle_click'):
        action.triggered.connect(module.handle_click)

def populate_menu(menu, path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            submenu = menu.addMenu(item)
            populate_menu(submenu, item_path)
        elif item.endswith('.py'):
            file_name, _ = os.path.splitext(item)  # 分离文件名和后缀
            action = menu.addAction(file_name)
            load_and_bind_action(action, item_path)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    # Populate the menu bar with the first-level directories under 'menu'
    root_menu_path = 'menu'
    if os.path.exists(root_menu_path) and os.path.isdir(root_menu_path):
        for folder in os.listdir(root_menu_path):
            folder_path = os.path.join(root_menu_path, folder)
            if os.path.isdir(folder_path):
                root_menu = ui.menubar.addMenu(folder)
                populate_menu(root_menu, folder_path)
    
    MainWindow.show()
    sys.exit(app.exec_())
