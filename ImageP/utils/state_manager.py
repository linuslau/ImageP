# state_manager.py

class StateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.selected_shape_type = "rectangle"  # 默认形状类型
            cls._instance.clear_previous_lines = False  # 默认不清除之前的线条
            cls._instance.image_data = None  # 添加图像数据的存储
        return cls._instance

    # 形状类型相关方法
    def set_shape_type(self, shape_type):
        self.selected_shape_type = shape_type

    def get_shape_type(self):
        return self.selected_shape_type

    # 清除之前线条相关方法
    def set_clear_previous_lines(self, clear):
        self.clear_previous_lines = clear

    def get_clear_previous_lines(self):
        return self.clear_previous_lines

    # 图像数据相关方法
    def set_image_data(self, image_data):
        self.image_data = image_data

    def get_image_data(self):
        return self.image_data

    def set_image_with_rect_instance(self, instance):
        self._image_with_rect_instance = instance

    def get_image_with_rect_instance(self):
        return self._image_with_rect_instance

# 方便的导出单例实例
state_manager = StateManager()
