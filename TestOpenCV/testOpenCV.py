import cv2
import tkinter as tk
from tkinter import messagebox
import threading
import numpy as np

# 全局变量
drawing = False  # 是否正在绘制
moving = False   # 是否正在移动
rect_start = None  # 矩形的起始点
rect_end = None    # 矩形的结束点
rects = []        # 存储矩形的列表
click_x, click_y = None, None  # 右键点击的位置

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

def handle_mouse_event(event, x, y, flags, param):
    global rect_start, rect_end, drawing, moving, rects, click_x, click_y

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
        if not drawing and not moving:
            # 检查是否点击在现有矩形上
            for rect in rects:
                if rect[0][0] <= x <= rect[1][0] and rect[0][1] <= y <= rect[1][1]:
                    moving = True
                    rect_start = (x, y)
                    return
            # 取消之前的矩形
            rects = []
            # 开始绘制新矩形
            drawing = True
            rect_start = (x, y)
            rect_end = (x, y)
        elif drawing:
            # 更新矩形的结束点
            rect_end = (x, y)
            temp_image = image.copy()
            for rect in rects:
                cv2.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)
            cv2.rectangle(temp_image, rect_start, rect_end, (0, 255, 0), 2)
            cv2.imshow('Image with Rectangle', temp_image)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # 实时显示矩形
            temp_image = image.copy()
            for rect in rects:
                cv2.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)
            cv2.rectangle(temp_image, rect_start, (x, y), (0, 255, 0), 2)
            cv2.imshow('Image with Rectangle', temp_image)
        elif moving:
            # 移动矩形
            dx, dy = x - rect_start[0], y - rect_start[1]
            for i in range(len(rects)):
                rects[i] = ((rects[i][0][0] + dx, rects[i][0][1] + dy),
                            (rects[i][1][0] + dx, rects[i][1][1] + dy))
            rect_start = (x, y)
            temp_image = image.copy()
            for rect in rects:
                cv2.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)
            cv2.imshow('Image with Rectangle', temp_image)
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing:
            # 完成绘制矩形
            drawing = False
            rect_end = (x, y)
            rects.append((rect_start, rect_end))
            temp_image = image.copy()
            for rect in rects:
                cv2.rectangle(temp_image, rect[0], rect[1], (0, 255, 0), 2)
            cv2.imshow('Image with Rectangle', temp_image)
        elif moving:
            # 完成移动矩形
            moving = False
            rect_end = (x, y)
            rect_start = (rect_start[0] + (x - rect_start[0]), rect_start[1] + (y - rect_start[1]))

# 读取图像
image = cv2.imread(r'./boats.jpg')
if image is None:
    raise ValueError("Failed to load image")

# 显示图像窗口
cv2.imshow('Image with Rectangle', image)

# 设置鼠标回调函数
cv2.setMouseCallback('Image with Rectangle', handle_mouse_event)

# 等待用户按键并关闭窗口
cv2.waitKey(0)
cv2.destroyAllWindows()
