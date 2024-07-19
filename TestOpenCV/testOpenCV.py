import cv2
import tkinter as tk
from tkinter import messagebox
import threading
import numpy as np
import ctypes
from ctypes import wintypes

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

# Windows API 设置鼠标指针
class Cursor:
    ARROW = 32512
    HAND = 32649

    @staticmethod
    def set_cursor(cursor_id):
        ctypes.windll.user32.SetCursor(ctypes.windll.user32.LoadCursorW(0, cursor_id))

def show_rect_info(rect):
    """弹出窗口显示矩形信息"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showinfo("Rectangle Info", f"Top-left: {rect[0]}\nBottom-right: {rect[1]}")
    root.destroy()

def show_gray_value(x, y):
    """计算并显示指定位置的灰度值"""
    global image
    # 转换为灰度图像
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 获取指定位置的灰度值
    gray_value = gray_image[y, x]
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showinfo("Gray Value", f"Gray Value at ({x}, {y}): {gray_value}")
    root.destroy()

def draw_rectangle(image, rect):
    """在图像上绘制矩形及其控制点"""
    temp_image = image.copy()
    cv2.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)
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
                        menu.add_command(label="Show Rectangle Info", command=lambda: show_rect_info(rect))
                        menu.add_command(label="Show Gray Value", command=lambda: show_gray_value(x, y))
                        menu.post(root.winfo_pointerx(), root.winfo_pointery())
                        root.mainloop()

                    # 使用主线程显示菜单
                    root_thread = threading.Thread(target=show_menu)
                    root_thread.start()
                    return

    elif event == cv2.EVENT_LBUTTONDOWN:
        if not drawing and not moving and not resizing:
            # 检查是否点击在现有矩形上
            for i, rect in enumerate(rects):
                if (rect[0][0] <= x <= rect[1][0] and rect[0][1] <= y <= rect[1][1]):
                    # 检查是否点击在控制点上
                    for j, point in enumerate(control_points):
                        if np.linalg.norm(np.array(point) - np.array((x, y))) <= 10:  # 增大阈值
                            resizing = True
                            current_rect_index = i
                            dragging_control_point = j
                            rect_start = (x, y)
                            return
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
        elif drawing:
            # 更新矩形的结束点
            rect_end = (x, y)
            temp_image = draw_rectangle(image, (rect_start, rect_end))
            cv2.imshow('Image with Rectangle', temp_image)
    elif event == cv2.EVENT_MOUSEMOVE:
        # 检查是否在控制点上
        if not drawing and not moving and not resizing:
            hovering_control_point = None
            for i, point in enumerate(control_points):
                if np.linalg.norm(np.array(point) - np.array((x, y))) <= 10:  # 增大阈值
                    hovering_control_point = i
                    break
            if hovering_control_point is not None:
                Cursor.set_cursor(Cursor.HAND)
            else:
                Cursor.set_cursor(Cursor.ARROW)
        if drawing:
            # 实时显示矩形
            temp_image = draw_rectangle(image, (rect_start, (x, y)))
            cv2.imshow('Image with Rectangle', temp_image)
        elif moving and current_rect_index is not None:
            # 移动矩形
            dx, dy = x - rect_start[0], y - rect_start[1]
            for i in range(len(rects)):
                if i == current_rect_index:
                    rects[i] = ((rects[i][0][0] + dx, rects[i][0][1] + dy),
                                (rects[i][1][0] + dx, rects[i][1][1] + dy))
            rect_start = (x, y)
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

# 读取图像
image = cv2.imread(r'boats.jpg')
if image is None:
    raise ValueError("Failed to load image")

# 显示图像窗口
cv2.imshow('Image with Rectangle', image)

# 设置鼠标回调函数
cv2.setMouseCallback('Image with Rectangle', handle_mouse_event)

# 等待用户按键并关闭窗口
cv2.waitKey(0)
cv2.destroyAllWindows()
