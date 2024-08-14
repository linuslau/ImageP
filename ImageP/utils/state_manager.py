# state_manager.py

class StateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.selected_shape_type = "rectangle"  # 默认形状类型
            cls._instance.clear_previous_lines = False  # 默认不清除之前的线条
        return cls._instance

    def set_shape_type(self, shape_type):
        self.selected_shape_type = shape_type

    def get_shape_type(self):
        return self.selected_shape_type

    def set_clear_previous_lines(self, clear):
        self.clear_previous_lines = clear

    def get_clear_previous_lines(self):
        return self.clear_previous_lines

# 方便的导出单例实例
state_manager = StateManager()
