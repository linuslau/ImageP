import os
import asyncio
import threading
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from ImageP.utils.state_manager import state_manager
from PyQt5.QtWidgets import QMessageBox

class IconManager(QObject):
    icon_clicked = pyqtSignal(int)  # Signal to notify icon index

    def __init__(self):
        super().__init__()
        self.current_clicked_action = None
        self.original_icons = {}
        self.icon_actions = []

    def add_icon_action(self, toolbar, icon_path, status_bar):
        if not os.path.isdir(icon_path):
            return
        folder_name = os.path.basename(icon_path)
        short_name = folder_name[:4]  # Get the first 4 characters of the folder name
        action = QAction(short_name, toolbar)
        self.icon_actions.append(action)

        # Check for image and Python files
        image_file = os.path.join(icon_path, 'image.jpg')
        py_file = os.path.join(icon_path, 'image.py')

        if os.path.exists(image_file) and os.path.exists(py_file):
            pixmap = QPixmap(image_file)
            if not pixmap.isNull():
                size = max(pixmap.width(), pixmap.height())
                icon = QIcon(pixmap.scaled(size, size))
                action.setIcon(icon)
                self.original_icons[action] = icon
                action.triggered.connect(
                    lambda checked=False, path=py_file, act=action: self.handle_icon_click(path, act))
        else:
            # If no image or Python file, set a default icon and no action
            default_icon = QIcon()  # You can set a default icon here if you have one
            action.setIcon(default_icon)
            action.triggered.connect(lambda: None)

        action.hovered.connect(lambda: status_bar.showMessage(os.path.basename(icon_path)))
        toolbar.addAction(action)

    def handle_icon_click(self, py_file, action):
        relative_path = os.path.relpath(py_file, os.path.join(os.path.dirname(__file__), '..'))
        module_name = relative_path.replace(os.path.sep, '.').replace('.py', '')

        try:
            # If the current action is clicked again, keep its gray color
            if self.current_clicked_action == action:
                print(f"Shape type {module_name} already selected and remains grey.")
            else:
                # If there is a previously clicked action, restore its color
                if self.current_clicked_action:
                    self.restore_icon_color(self.current_clicked_action)
                self.gray_out_icon(action)
                self.current_clicked_action = action

            # Emit the signal with the index of the clicked action
            index = self.icon_actions.index(action)
            self.icon_clicked.emit(index)

            # Call the menu click handling logic
            handle_menu_click(action.parentWidget().parent(), py_file)

        except ModuleNotFoundError as e:
            print(f"Module not found: {e}")
        except Exception as e:
            print(f"Error while handling icon click: {e}")

    def gray_out_icon(self, action):
        icon = action.icon()
        pixmap = icon.pixmap(32, 32)
        image = pixmap.toImage()
        for i in range(image.width()):
            for j in range(image.height()):
                color = image.pixelColor(i, j)
                gray = int(color.red() * 0.3 + color.green() * 0.59 + color.blue() * 0.11)
                color.setRed(gray)
                color.setGreen(gray)
                color.setBlue(gray)
                image.setPixelColor(i, j, color)
        action.setIcon(QIcon(QPixmap.fromImage(image)))

    def restore_icon_color(self, action):
        if action in self.original_icons:
            action.setIcon(self.original_icons[action])

    def gray_out_first_icon(self):
        if self.icon_actions:
            first_action = self.icon_actions[0]
            self.gray_out_icon(first_action)
            self.current_clicked_action = first_action
            self.icon_clicked.emit(0)


def load_menu_order(menu_path):
    order_file_path = os.path.join(menu_path, 'order.txt')
    if os.path.exists(order_file_path):
        with open(order_file_path, 'r') as order_file:
            return [line.strip() for line in order_file.readlines() if line.strip()]
    return []


def load_shortcut(file_path):
    shortcut_file_path = os.path.splitext(file_path)[0] + '.txt'
    if os.path.exists(shortcut_file_path):
        with open(shortcut_file_path, 'r') as shortcut_file:
            return shortcut_file.readline().strip()
    return None


def load_icon(file_path):
    icon_file_path = os.path.splitext(file_path)[0] + '.png'
    if os.path.exists(icon_file_path):
        pixmap = QPixmap(icon_file_path)
        if not pixmap.isNull():
            size = max(pixmap.width(), pixmap.height())
            return QIcon(pixmap.scaled(size, size, Qt.KeepAspectRatio))
    return None


def populate_icons(toolbar, icons_path, status_bar, icon_manager):
    # Load the order from order.txt
    items = os.listdir(icons_path)
    ordered_items = load_menu_order(icons_path)
    combined_items = ordered_items + [item for item in items if item not in ordered_items]

    for item in combined_items:
        item_path = os.path.join(icons_path, item)
        if os.path.isdir(item_path):
            icon_manager.add_icon_action(toolbar, item_path, status_bar)

    icon_manager.gray_out_first_icon()


def populate_menu(menu, folder_path, status_bar):
    ordered_items = load_menu_order(folder_path)
    items = os.listdir(folder_path)
    combined_items = ordered_items + [item for item in items if item not in ordered_items]

    for item in combined_items:
        if item == '-':
            menu.addSeparator()
            continue
        item_path = os.path.join(folder_path, item)
        if item == '__pycache__':
            continue
        if os.path.isdir(item_path):
            sub_menu = menu.addMenu(item)

            # Load sub-menu icon
            icon = load_icon(item_path)
            if icon:
                sub_menu.setIcon(icon)

            populate_menu(sub_menu, item_path, status_bar)
        elif item.endswith('.py') and item != '__init__.py':
            action_text = item.replace('.py', '')
            action = QAction(action_text, menu)

            # Load shortcut
            shortcut = load_shortcut(item_path)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
                action_text_with_shortcut = f"{action_text} ({shortcut})"
                action.setText(action_text_with_shortcut)
            else:
                action.setText(action_text)

            # Load icon
            icon = load_icon(item_path)
            if icon:
                action.setIcon(icon)

            action.triggered.connect(lambda checked=False, path=item_path: handle_menu_click(menu.parentWidget().parent(), path))
            action.hovered.connect(lambda: status_bar.showMessage(action.text()))
            menu.addAction(action)


def handle_menu_click(main_window, file_path):
    try:
        print(f"handle_menu_click triggered with file_path: {file_path}")
        relative_path = os.path.relpath(file_path, os.path.join(os.path.dirname(__file__), '..'))
        module_name = relative_path.replace(os.path.sep, '.').replace('.py', '')
        print(f"Module name: {module_name}")

        # Load the module and call its functions
        module_spec = __import__(module_name, fromlist=[module_name])

        # First handle synchronous methods
        if hasattr(module_spec, 'menu_click'):
            print("Calling menu_click")
            module_spec.menu_click()

        if hasattr(module_spec, 'handle_click'):
            print("Calling handle_click")
            module_spec.handle_click()

        # Then handle asynchronous methods
        loop = asyncio.get_event_loop()

        async def run_async_tasks():
            if hasattr(module_spec, 'menu_click_async'):
                print("Starting async task for menu_click_async")
                await module_spec.menu_click_async()

            if hasattr(module_spec, 'handle_click_async'):
                print("Starting async task for handle_click_async")
                await module_spec.handle_click_async()

        # If there are async tasks, execute them
        if hasattr(module_spec, 'menu_click_async') or hasattr(module_spec, 'handle_click_async'):
            loop.create_task(run_async_tasks())

        # Function to handle asynchronous tasks in a thread
        def run_async_tasks():
            if hasattr(module_spec, 'menu_click_thread'):
                print("Starting thread task for menu_click_thread")
                module_spec.menu_click_thread()  # Assuming this can be run without 'await'

            if hasattr(module_spec, 'handle_click_thread'):
                print("Starting thread task for handle_click_thread")
                module_spec.handle_click_thread()  # Assuming this can be run without 'await'

        # If there are async tasks, execute them in a new thread
        if hasattr(module_spec, 'menu_click_thread') or hasattr(module_spec, 'handle_click_thread'):
            async_thread = threading.Thread(target=run_async_tasks)
            async_thread.start()

        async def process_and_update_ui():
            image_data = state_manager.get_image_data()  # 获取当前图像数据
            inverted_image = None

            # 判断是2D还是3D图像
            if len(image_data.shape) == 3:  # 3D图像
                # 获取当前选中的图层索引
                current_layer = state_manager.get_image_with_rect_instance().slider.value()

                # 弹出对话框
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Process Stack?")
                msg_box.setText(f"Process all {image_data.shape[0]} images? There is no Undo if you select 'Yes'.")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                msg_box.setDefaultButton(QMessageBox.No)
                ret = msg_box.exec_()

                if ret == QMessageBox.Yes:
                    # 用户选择Yes，处理所有图层
                    print("Processing all layers of the 3D image...")
                    for layer in range(image_data.shape[0]):
                        current_layer_image = image_data[layer]
                        inverted_image_layer = await module_spec.process_image_async(current_layer_image)
                        image_data[layer] = inverted_image_layer  # 更新每一层

                    state_manager.set_image_data(image_data)
                    image_with_rect = state_manager.get_image_with_rect_instance()

                    # 更新UI显示用户最初选择的图层，而不是跳到第一层
                    image_with_rect.update_image_with_data(image_data[current_layer])
                    image_with_rect.slider.setValue(current_layer)  # 保持slider选中的图层

                elif ret == QMessageBox.No:
                    # 用户选择No，只处理当前选中的图层
                    print(f"Processing current layer {current_layer} of the 3D image...")
                    current_layer_image = image_data[current_layer]
                    inverted_image_layer = await module_spec.process_image_async(current_layer_image)

                    # 更新3D图像中的当前图层
                    image_data[current_layer] = inverted_image_layer

                    # 更新UI，显示当前处理后的图层
                    state_manager.set_image_data(image_data)
                    image_with_rect = state_manager.get_image_with_rect_instance()
                    image_with_rect.update_image_with_data(image_data[current_layer])

            elif len(image_data.shape) == 2:  # 2D图像
                print("Processing 2D image")
                if hasattr(module_spec, 'process_image_async'):
                    # 直接处理2D图像
                    inverted_image = await module_spec.process_image_async(image_data)

                    # 更新图像数据到全局状态管理器中
                    state_manager.set_image_data(inverted_image)
                    image_with_rect = state_manager.get_image_with_rect_instance()
                    image_with_rect.update_image_with_data(inverted_image)

        if hasattr(module_spec, 'process_image_async'):
            # 开始异步处理图片并更新UI
            loop.create_task(process_and_update_ui())

    except ModuleNotFoundError as e:
        print(f"Module not found: {e}")
    except Exception as e:
        print(f"Error in handle_menu_click: {e}")
