from PyQt5 import QtWidgets
from ImageP.ui.main_ui_qt5 import Ui_MainWindow
from ImageP.utils.menu_populate import populate_menu
import sys
import os


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
        for folder in os.listdir(root_menu_path):
            folder_path = os.path.join(root_menu_path, folder)
            if os.path.isdir(folder_path):
                root_menu = ui.menubar.addMenu(folder)
                populate_menu(root_menu, folder_path)

    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
