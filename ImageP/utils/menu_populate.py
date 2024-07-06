import os
from PyQt5.QtWidgets import QAction


def load_menu_order(menu_path):
    order_file_path = os.path.join(menu_path, 'order.txt')
    if os.path.exists(order_file_path):
        with open(order_file_path, 'r') as order_file:
            return [line.strip() for line in order_file.readlines() if line.strip()]
    return []


def populate_menu(menu, folder_path, is_root=False):
    ordered_items = load_menu_order(folder_path)

    items = os.listdir(folder_path)
    items = sorted(items, key=lambda x: (ordered_items.index(x) if x in ordered_items else float('inf'), x))

    for item in items:
        item_path = os.path.join(folder_path, item)
        if item == '__pycache__':
            continue
        if os.path.isdir(item_path):
            sub_menu = menu.addMenu(item)
            populate_menu(sub_menu, item_path)
        elif item.endswith('.py') and item != '__init__.py':
            action = QAction(item.replace('.py', ''), menu)
            action.triggered.connect(lambda checked, path=item_path: handle_menu_click(path))
            menu.addAction(action)


def handle_menu_click(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    module_spec = __import__('menu.' + module_name, fromlist=[module_name])
    if hasattr(module_spec, 'menu_click'):
        window = module_spec.menu_click()
        if window:
            window.show()
