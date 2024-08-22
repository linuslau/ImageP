import sys
import os
import asyncio
from PyQt5 import QtWidgets, QtCore
from qasync import QEventLoop
from ui.main_ui_qt5 import Ui_MainWindow
from utils.menu_populate import populate_menu, populate_icons, load_menu_order, IconManager, handle_menu_click

class MainWindow(QtWidgets.QMainWindow):
    icon_clicked = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()

    def initUI(self):
        # Get the path of the current script file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Locate the menu directory in the installation path
        root_menu_path = os.path.join(script_dir, 'menu')

        # Getting the root icons path
        icons_path = os.path.join(os.path.dirname(__file__), 'icons')
        print(f"Root icons path: {icons_path}")

        # If the path does not exist, try to find it from the package installation directory
        if not os.path.exists(root_menu_path):
            root_menu_path = os.path.join(os.path.dirname(__file__), 'menu')

        print(f"Root menu path: {root_menu_path}")

        if os.path.exists(root_menu_path) and os.path.isdir(root_menu_path):
            # Get the order of menu items
            ordered_items = load_menu_order(root_menu_path)

            # Get all folders and files and add them in order
            for item in ordered_items:
                if item == '-':
                    self.ui.menubar.addSeparator()
                else:
                    item_path = os.path.join(root_menu_path, item)
                    if (os.path.isdir(item_path) and item != '__pycache__') or (item.endswith('.py') and item != '__init__.py'):
                        self.add_menu_item(self.ui.menubar, item_path, os.path.isdir(item_path), self.ui.statusbar)

        # Initialize IconManager
        self.icon_manager = IconManager()
        self.icon_manager.icon_clicked.connect(self.on_icon_clicked)

        # Check if the icons directory exists
        if os.path.exists(icons_path) and os.path.isdir(icons_path):
            populate_icons(self.ui.toolBar, icons_path, self.ui.statusbar, self.icon_manager)

        self.ui.statusbar.showMessage("Welcome to use ImageP")

    def add_menu_item(self, parent_menu, path, is_folder, status_bar):
        print(f"Adding menu item for {path}")
        if is_folder:
            sub_menu = parent_menu.addMenu(os.path.basename(path))
            print(f"Creating submenu for {os.path.basename(path)}")
            populate_menu(sub_menu, path, status_bar)
        else:
            print(f"Creating menu item for {os.path.basename(path)}")
            action = parent_menu.addAction(os.path.basename(path).replace('.py', ''))
            print(f"Connecting {action.text()} to handle_menu_click")
            action.triggered.connect(lambda: handle_menu_click(path))
            action.hovered.connect(lambda: status_bar.showMessage(os.path.basename(path).replace('.py', '')))
            parent_menu.addAction(action)

    def on_icon_clicked(self, index):
        print(f"Icon clicked with index: {index}")
        self.icon_clicked.emit(index)

    def leaveEvent(self, event):
        self.ui.statusbar.showMessage("Welcome to use ImageP")
        super().leaveEvent(event)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.HoverEnter and isinstance(source, QtWidgets.QAction):
            self.ui.statusbar.showMessage(source.text())
        return super().eventFilter(source, event)

def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    main_window = MainWindow()
    main_window.setWindowTitle("ImageP")
    main_window.show()

    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main()
