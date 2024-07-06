import os
import importlib.util

def load_and_bind_action(action, module_path):
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, 'handle_click'):
        action.triggered.connect(module.handle_click)

def populate_menu(menu, path):
    print(f"Populating menu: {path}")
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            if item == '__pycache__':
                continue  # 忽略 __pycache__ 目录
            print(f"Adding submenu for directory: {item_path}")
            submenu = menu.addMenu(item)
            populate_menu(submenu, item_path)
        elif item.endswith('.py'):
            file_name, _ = os.path.splitext(item)  # 分离文件名和后缀
            print(f"Adding action for file: {item_path}")
            action = menu.addAction(file_name)
            load_and_bind_action(action, item_path)
