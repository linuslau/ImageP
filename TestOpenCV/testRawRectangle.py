import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np
import ctypes
import time
import os

# 全局变量
drawing = False  # 是否正在绘制
moving = False  # 是否正在移动
resizing = False  # 是否正在调整大小
rect_start = None  # 矩形的起始点
rect_end = None  # 矩形的结束点
rects = []  # 存储矩形的列表
click_x, click_y = None, None  # 右键点击的位置
control_points = []  # 控制点的列表
current_rect_index = None  # 当前正在调整大小的矩形索引
dragging_control_point = None  # 当前正在拖动的控制点
hovering_control_point = None  # 当前悬停的控制点
image = None

# Windows API 设置鼠标指针
class Cursor:
    ARROW = 32512
    HAND = 32649

    @staticmethod
    def set_cursor(cursor_id):
        ctypes.windll.user32.SetCursor(ctypes.windll.user32.LoadCursorW(0, cursor_id))


def open_raw_file(filename, image_type, width, height, offset):
    dtype_map = {
        '8-bit': np.uint8,
        '16-bit Signed': np.int16,
        '16-bit Unsigned': np.uint16,
        '32-bit Signed': np.int32,
        '32-bit Unsigned': np.uint32,
        '32-bit Real': np.float32,
        '64-bit Real': np.float64,
        '24-bit RGB': np.uint8  # Special handling needed for RGB
    }

    dtype = dtype_map[image_type]

    with open(filename, 'rb') as file:
        file.seek(offset)
        if image_type == '24-bit RGB':
            img = np.fromfile(file, dtype=dtype, count=width * height * 3).reshape((height, width, 3))
        else:
            img = np.fromfile(file, dtype=dtype, count=width * height).reshape((height, width))

    return img


def open_file_dialog():
    start_time = time.time()
    filename = filedialog.askopenfilename(title="Select RAW file",
                                          filetypes=[("RAW files", "*.raw"), ("All files", "*.*")])
    file_dialog_time = time.time()
    print(f"File dialog time: {file_dialog_time - start_time:.2f} seconds")

    if filename:
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext == '.raw':
            open_settings_dialog(filename)
        else:
            global image
            image = cv2.imread(filename)
            if image is None:
                messagebox.showerror("Error", "Failed to load image")
                return
            cv2.imshow('Image with Rectangle', image)
            cv2.setMouseCallback('Image with Rectangle', handle_mouse_event)


def open_settings_dialog(filename):
    start_time = time.time()
    settings_dialog = tk.Toplevel()
    settings_dialog.title("Import RAW...")

    tk.Label(settings_dialog, text="Image type:").grid(row=0, column=0, sticky="e")
    image_type_var = tk.StringVar()
    image_type_combobox = ttk.Combobox(settings_dialog, textvariable=image_type_var)
    image_type_combobox['values'] = ('8-bit', '16-bit Signed', '16-bit Unsigned', '32-bit Signed',
                                     '32-bit Unsigned', '32-bit Real', '64-bit Real', '24-bit RGB')
    image_type_combobox.current(0)
    image_type_combobox.grid(row=0, column=1)

    tk.Label(settings_dialog, text="Width:").grid(row=1, column=0, sticky="e")
    width_entry = tk.Entry(settings_dialog)
    width_entry.grid(row=1, column=1)
    width_entry.insert(0, "720")

    tk.Label(settings_dialog, text="Height:").grid(row=2, column=0, sticky="e")
    height_entry = tk.Entry(settings_dialog)
    height_entry.grid(row=2, column=1)
    height_entry.insert(0, "576")

    tk.Label(settings_dialog, text="Offset to first image:").grid(row=3, column=0, sticky="e")
    offset_entry = tk.Entry(settings_dialog)
    offset_entry.grid(row=3, column=1)
    offset_entry.insert(0, "0")

    tk.Label(settings_dialog, text="Number of images:").grid(row=4, column=0, sticky="e")
    num_images_entry = tk.Entry(settings_dialog)
    num_images_entry.grid(row=4, column=1)
    num_images_entry.insert(0, "1")

    tk.Label(settings_dialog, text="Gap between images:").grid(row=5, column=0, sticky="e")
    gap_entry = tk.Entry(settings_dialog)
    gap_entry.grid(row=5, column=1)
    gap_entry.insert(0, "0")

    white_is_zero_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="White is zero", variable=white_is_zero_var).grid(row=6, column=0, sticky="w",
                                                                                           columnspan=2)

    little_endian_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="Little-endian byte order", variable=little_endian_var).grid(row=7, column=0,
                                                                                                      sticky="w",
                                                                                                      columnspan=2)

    open_all_files_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="Open all files in folder", variable=open_all_files_var).grid(row=8, column=0,
                                                                                                       sticky="w",
                                                                                                       columnspan=2)

    use_virtual_stack_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="Use virtual stack", variable=use_virtual_stack_var).grid(row=9, column=0,
                                                                                                   sticky="w",
                                                                                                   columnspan=2)

    def on_ok():
        global image
        try:
            image_type = image_type_var.get()
            width = int(width_entry.get())
            height = int(height_entry.get())
            offset = int(offset_entry.get())

            image = open_raw_file(filename, image_type, width, height, offset)

            # 如果图像是单通道的（灰度图像），将其转换为三通道的伪彩色图像
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            cv2.imshow('Image with Rectangle', image)
            cv2.setMouseCallback('Image with Rectangle', handle_mouse_event)

            settings_dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    tk.Button(settings_dialog, text="OK", command=on_ok).grid(row=10, column=0, sticky="e")
    tk.Button(settings_dialog, text="Cancel", command=settings_dialog.destroy).grid(row=10, column=1, sticky="w")

    settings_dialog_time = time.time()
    print(f"Settings dialog time: {settings_dialog_time - start_time:.2f} seconds")

# 其余代码保持不变


def show_rect_properties(rect):
    """弹出窗口显示矩形属性"""

    def on_ok():
        # 获取输入框的内容
        name = name_entry.get()
        position = position_entry.get()
        group = group_entry.get()
        stroke_color = stroke_color_entry.get()
        width = width_entry.get()
        fill_color = fill_color_entry.get()
        list_coordinates = list_coordinates_var.get()

        # 打印输入框的内容和复选框的状态
        print(f"Name: {name}")
        print(f"Position: {position}")
        print(f"Group: {group}")
        print(f"Stroke color: {stroke_color}")
        print(f"Width: {width}")
        print(f"Fill color: {fill_color}")
        print(f"List coordinates: {list_coordinates}")

        root.destroy()

    def on_cancel():
        root.destroy()

    root = tk.Tk()
    root.title("ROW Properties")

    # 创建并排列标签和输入框
    tk.Label(root, text="Name").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Position").grid(row=1, column=0, padx=5, pady=5)
    position_entry = tk.Entry(root)
    position_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="Group").grid(row=2, column=0, padx=5, pady=5)
    group_entry = tk.Entry(root)
    group_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(root, text="Stroke color").grid(row=3, column=0, padx=5, pady=5)
    stroke_color_entry = tk.Entry(root)
    stroke_color_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(root, text="Width").grid(row=4, column=0, padx=5, pady=5)
    width_entry = tk.Entry(root)
    width_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(root, text="Fill color").grid(row=5, column=0, padx=5, pady=5)
    fill_color_entry = tk.Entry(root)
    fill_color_entry.grid(row=5, column=1, padx=5, pady=5)

    # 创建并排列复选框
    list_coordinates_var = tk.BooleanVar()
    list_coordinates_checkbox = tk.Checkbutton(root, text="List coordinates (4)", variable=list_coordinates_var)
    list_coordinates_checkbox.grid(row=6, columnspan=2, padx=5, pady=5)

    # 创建并排列按钮
    ok_button = tk.Button(root, text="OK", command=on_ok)
    ok_button.grid(row=7, column=0, padx=5, pady=5, sticky='e')
    cancel_button = tk.Button(root, text="Cancel", command=on_cancel)
    cancel_button.grid(row=7, column=1, padx=5, pady=5, sticky='w')

    root.mainloop()


def show_measure_menu():
    """弹出窗口显示 Measure 菜单"""
    def on_ok():
        root.destroy()

    def on_cancel():
        root.destroy()

    def calculate_metrics(rect):
        """计算矩形区域的灰度值统计信息"""
        x1, y1 = rect[0]
        x2, y2 = rect[1]
        # 裁剪出矩形区域
        roi = image[y1:y2, x1:x2]
        # 检查图像通道数
        if len(roi.shape) == 3:
            # 转换为灰度图像
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray_roi = roi
        # 计算统计信息
        area = gray_roi.size
        mean = np.mean(gray_roi)
        min_val = np.min(gray_roi)
        max_val = np.max(gray_roi)
        return area, mean, min_val, max_val

    def update_table(rect):
        """更新表格中的数据"""
        area, mean, min_val, max_val = calculate_metrics(rect)
        # 如果表格没有行，则插入新行
        if not table.get_children():
            table.insert('', 'end', iid=1, values=(area, f'{mean:.2f}', min_val, max_val))
        else:
            table.item(1, values=(area, f'{mean:.2f}', min_val, max_val))

    root = tk.Tk()
    root.title("Measure")

    # 创建菜单栏
    menu_bar = tk.Menu(root)

    # File 菜单
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New", command=lambda: print("New"))
    file_menu.add_command(label="Open", command=lambda: print("Open"))
    file_menu.add_separator()
    file_menu.add_command(label="Save", command=lambda: print("Save"))
    file_menu.add_command(label="Save As...", command=lambda: print("Save As"))
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Edit 菜单
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Undo", command=lambda: print("Undo"))
    edit_menu.add_command(label="Redo", command=lambda: print("Redo"))
    edit_menu.add_separator()
    edit_menu.add_command(label="Cut", command=lambda: print("Cut"))
    edit_menu.add_command(label="Copy", command=lambda: print("Copy"))
    edit_menu.add_command(label="Paste", command=lambda: print("Paste"))
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # Font 菜单
    font_menu = tk.Menu(menu_bar, tearoff=0)
    font_menu.add_command(label="Bold", command=lambda: print("Bold"))
    font_menu.add_command(label="Italic", command=lambda: print("Italic"))
    font_menu.add_separator()
    font_menu.add_command(label="Underline", command=lambda: print("Underline"))
    menu_bar.add_cascade(label="Font", menu=font_menu)

    # Results 菜单
    results_menu = tk.Menu(menu_bar, tearoff=0)
    results_menu.add_command(label="Summary", command=lambda: print("Summary"))
    results_menu.add_command(label="Details", command=lambda: print("Details"))
    menu_bar.add_cascade(label="Results", menu=results_menu)

    # 显示菜单栏
    root.config(menu=menu_bar)

    # 创建表格
    table_frame = tk.Frame(root)
    table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    table = ttk.Treeview(table_frame, columns=('Area', 'Mean', 'Min', 'Max'), show='headings')
    table.heading('Area', text='Area')
    table.heading('Mean', text='Mean')
    table.heading('Min', text='Min')
    table.heading('Max', text='Max')

    # 初始行
    table.insert('', 'end', iid=1, values=('0', '0', '0', '0'))
    table.pack(fill=tk.BOTH, expand=True)

    # 更新表格数据
    if rects:
        update_table(rects[-1])

    # 创建并排列按钮
    ok_button = tk.Button(root, text="OK", command=on_ok)
    ok_button.pack(side=tk.LEFT, padx=5, pady=5)
    cancel_button = tk.Button(root, text="Cancel", command=on_cancel)
    cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

    root.mainloop()


def draw_rectangle(image, rect):
    """在图像上绘制矩形"""
    temp_image = image.copy()
    pt1, pt2 = rect
    cv2.rectangle(temp_image, pt1, pt2, (0, 255, 0), 2)
    for point in control_points:
        cv2.circle(temp_image, point, 5, (0, 0, 255), -1)
    return temp_image


def update_control_points(rect):
    """更新控制点的位置"""
    global control_points
    x1, y1 = rect[0]
    x2, y2 = rect[1]
    control_points = [
        (x1, y1),  # Top-left
        (x2, y1),  # Top-right
        (x1, y2),  # Bottom-left
        (x2, y2),  # Bottom-right
        ((x1 + x2) // 2, y1),  # Top-center
        ((x1 + x2) // 2, y2),  # Bottom-center
        (x1, (y1 + y2) // 2),  # Left-center
        (x2, (y1 + y2) // 2)  # Right-center
    ]


def handle_mouse_event(event, x, y, flags, param):
    global rect_start, rect_end, drawing, moving, resizing, rects, click_x, click_y, control_points, current_rect_index, dragging_control_point, hovering_control_point

    if event == cv2.EVENT_RBUTTONDOWN:
        click_x, click_y = x, y  # 保存右键点击的位置
        if rects:
            for rect in rects:
                if rect[0][0] <= x <= rect[1][0] and rect[0][1] <= y <= rect[1][1]:
                    # 在 Tkinter 主线程中显示菜单
                    def show_menu():
                        root = tk.Tk()
                        root.withdraw()  # 隐藏主窗口
                        menu = tk.Menu(root, tearoff=0)
                        menu.add_command(label="ROW Properties", command=lambda: show_rect_properties(rect))
                        menu.add_separator()
                        menu.add_command(label="Measure", command=show_measure_menu)
                        menu.post(root.winfo_pointerx(), root.winfo_pointery())
                        root.mainloop()

                    # 使用主线程显示菜单
                    threading.Thread(target=show_menu).start()
                    break
    elif event == cv2.EVENT_LBUTTONDOWN:
        for i, rect in enumerate(rects):
            # 检查是否在控制点上点击
            for j, point in enumerate(control_points):
                if np.linalg.norm(np.array(point) - np.array((x, y))) <= 10:  # 增大阈值
                    resizing = True
                    current_rect_index = i
                    dragging_control_point = j
                    rect_start = (x, y)
                    return
            # 检查是否在矩形内部点击
            if rect[0][0] <= x <= rect[1][0] and rect[0][1] <= y <= rect[1][1]:
                moving = True
                current_rect_index = i
                rect_start = (x, y)
                return
        # 取消之前的矩形
        rects = []
        control_points = []
        # 开始绘制新矩形
        drawing = True
        rect_start = (x, y)
        rect_end = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        # 检查是否在控制点上
        if not drawing and not moving and not resizing:
            hovering_control_point = None
            for i, point in enumerate(control_points):
                if np.linalg.norm(np.array(point) - np.array((x, y))) <= 10:  # 墛大阈值
                    hovering_control_point = i
                    break
            if hovering_control_point is not None:
                Cursor.set_cursor(Cursor.HAND)
            else:
                Cursor.set_cursor(Cursor.ARROW)
        if drawing:
            # 实时显示矩形
            rect_end = (x, y)
            temp_image = draw_rectangle(image, (rect_start, rect_end))
            cv2.imshow('Image with Rectangle', temp_image)
        elif moving and current_rect_index is not None:
            # 移动矩形
            dx, dy = x - rect_start[0], y - rect_start[1]
            rect_start = (x, y)
            rects[current_rect_index] = ((rects[current_rect_index][0][0] + dx, rects[current_rect_index][0][1] + dy),
                                         (rects[current_rect_index][1][0] + dx, rects[current_rect_index][1][1] + dy))
            update_control_points(rects[current_rect_index])
            temp_image = draw_rectangle(image, rects[current_rect_index])
            cv2.imshow('Image with Rectangle', temp_image)
        elif resizing and current_rect_index is not None and dragging_control_point is not None:
            # 调整矩形大小
            rect = rects[current_rect_index]
            x1, y1 = rect[0]
            x2, y2 = rect[1]

            if dragging_control_point == 0:  # Top-left
                x1, y1 = x, y
            elif dragging_control_point == 1:  # Top-right
                x2, y1 = x, y
            elif dragging_control_point == 2:  # Bottom-left
                x1, y2 = x, y
            elif dragging_control_point == 3:  # Bottom-right
                x2, y2 = x, y
            elif dragging_control_point == 4:  # Top-center
                y1 = y
            elif dragging_control_point == 5:  # Bottom-center
                y2 = y
            elif dragging_control_point == 6:  # Left-center
                x1 = x
            elif dragging_control_point == 7:  # Right-center
                x2 = x

            # 更新矩形
            rects[current_rect_index] = ((x1, y1), (x2, y2))
            update_control_points(rects[current_rect_index])
            temp_image = draw_rectangle(image, rects[current_rect_index])
            cv2.imshow('Image with Rectangle', temp_image)
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing:
            # 完成绘制矩形
            drawing = False
            rect_end = (x, y)
            rects.append((rect_start, rect_end))
            update_control_points(rects[-1])
            temp_image = draw_rectangle(image, rects[-1])
            cv2.imshow('Image with Rectangle', temp_image)
        elif moving:
            # 完成移动矩形
            moving = False
            rect_start = None
        elif resizing:
            # 完成调整大小
            resizing = False
            dragging_control_point = None
            rect_start = None


def main():
    root = tk.Tk()
    root.withdraw()
    open_file_dialog()
    root.mainloop()

    if image is None:
        raise ValueError("Failed to load image")

    # 显示图像窗口
    cv2.imshow('Image with Rectangle', image)

    # 设置鼠标回调函数
    cv2.setMouseCallback('Image with Rectangle', handle_mouse_event)

    # 等待用户按键并关闭窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
