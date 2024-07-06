import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

def load_menu_order(menu_path):
    order_file_path = os.path.join(menu_path, 'order.txt')
    if os.path.exists(order_file_path):
        with open(order_file_path, 'r') as order_file:
            return [line.strip() for line in order_file.readlines() if line.strip()]
    return []

def populate_icons(toolbar, icons_path, status_bar):
    items = os.listdir(icons_path)
    ordered_items = load_menu_order(icons_path)

    items = sorted(items, key=lambda x: (ordered_items.index(x) if x in ordered_items else float('inf'), x))

    for item in items:
        item_path = os.path.join(icons_path, item)
        if os.path.isdir(item_path):
            add_icon_action(toolbar, item_path, status_bar)

def populate_menu(menu, folder_path, status_bar):
    ordered_items = load_menu_order(folder_path)

    items = os.listdir(folder_path)
    items = sorted(items, key=lambda x: (ordered_items.index(x) if x in ordered_items else float('inf'), x))

    for item in items:
        item_path = os.path.join(folder_path, item)
        if item == '__pycache__':
            continue
        if os.path.isdir(item_path):
            sub_menu = menu.addMenu(item)
            populate_menu(sub_menu, item_path, status_bar)
        elif item.endswith('.py') and item != '__init__.py':
            action = QAction(item.replace('.py', ''), menu)
            action.triggered.connect(lambda checked, path=item_path: handle_menu_click(path))
            action.hovered.connect(lambda: status_bar.showMessage(item.replace('.py', '')))
            menu.addAction(action)

def add_icon_action(toolbar, icon_path, status_bar):
    if not os.path.isdir(icon_path):
        return
    image_file = os.path.join(icon_path, 'image.jpg')
    py_file = os.path.join(icon_path, 'image.py')

    if os.path.exists(image_file) and os.path.exists(py_file):
        action = QAction(QIcon(image_file), os.path.basename(icon_path), toolbar)
        action.triggered.connect(lambda: handle_icon_click(py_file))
        action.hovered.connect(lambda: status_bar.showMessage(os.path.basename(icon_path)))
        toolbar.addAction(action)

def handle_menu_click(file_path):
    relative_path = os.path.relpath(file_path, os.path.join(os.path.dirname(__file__), '..'))
    module_name = 'ImageP.' + relative_path.replace(os.path.sep, '.').replace('.py', '')
    try:
        module_spec = __import__(module_name, fromlist=[module_name.split('.')[-1]])
        if hasattr(module_spec, 'handle_click'):
            module_spec.handle_click()
    except ModuleNotFoundError as e:
        print(f"Module not found: {e}")
    except Exception as e:
        print(f"Error while handling menu click: {e}")

def handle_icon_click(py_file):
    relative_path = os.path.relpath(py_file, os.path.join(os.path.dirname(__file__), '..'))
    module_name = 'ImageP.' + relative_path.replace(os.path.sep, '.').replace('.py', '')
    try:
        module_spec = __import__(module_name, fromlist=[module_name])
        if hasattr(module_spec, 'handle_click'):
            module_spec.handle_click()
    except ModuleNotFoundError as e:
        print(f"Module not found: {e}")
    except Exception as e:
        print(f"Error while handling icon click: {e}")
