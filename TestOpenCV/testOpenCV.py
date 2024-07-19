import cv2

# 全局变量
drawing = False  # 是否正在绘制
ix, iy = -1, -1  # 矩形的起始点

# 鼠标回调函数
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        # 鼠标左键按下时记录起始点
        ix, iy = x, y
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # 绘制矩形
            temp_image = image.copy()
            cv2.rectangle(temp_image, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('Image with Rectangle', temp_image)
    elif event == cv2.EVENT_LBUTTONUP:
        # 鼠标左键松开时结束绘制
        drawing = False
        cv2.rectangle(image, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('Image with Rectangle', image)

# 读取图像
image = cv2.imread(r'image.jpg')
if image is None:
    raise ValueError("Failed to load image")

# 显示图像窗口
cv2.imshow('Image with Rectangle', image)

# 设置鼠标回调函数
cv2.setMouseCallback('Image with Rectangle', draw_rectangle)

# 等待用户按键并关闭窗口
cv2.waitKey(0)
cv2.destroyAllWindows()
