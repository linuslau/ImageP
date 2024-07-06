import os
import importlib.util
from PyQt5.QtWidgets import QAction


def load_menu_order(menu_path):
    order_file_path = os.path.join(menu_path, 'order.txt')
    if os.path.exists(order_file_path):
        with open(order_file_path, 'r') as order_file:
            return [line.strip() for line in order_file.readlines() if line.strip()]
    return []


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
            sub_menu.hovered.connect(lambda: status_bar.showMessage(f'Hovering over {item}'))
            populate_menu(sub_menu, item_path, status_bar)
        elif item.endswith('.py') and item != '__init__.py':
            action = QAction(item.replace('.py', ''), menu)
            action.triggered.connect(lambda checked, path=item_path: handle_menu_click(path, status_bar))
            action.hovered.connect(lambda: status_bar.showMessage(f'Hovering over {item}'))
            menu.addAction(action)


def handle_menu_click(file_path, status_bar):
    relative_path = os.path.relpath(file_path, os.path.join(os.path.dirname(__file__), '..'))
    module_name = 'ImageP.' + relative_path.replace(os.path.sep, '.').replace('.py', '')
    try:
        module_spec = __import__(module_name, fromlist=[module_name.split('.')[-1]])
        if hasattr(module_spec, 'handle_click'):
            module_spec.handle_click()
    except ModuleNotFoundError as e:
        status_bar.showMessage(f"Module not found: {e}")
    except Exception as e:
        status_bar.showMessage(f"Error while handling menu click: {e}")
