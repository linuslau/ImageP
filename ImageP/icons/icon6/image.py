from ImageP.utils.state_manager import state_manager
def handle_click():
    print("icon6/image clicked")
    state_manager.set_shape_type("dynamic_line")
    state_manager.set_clear_previous_lines(True)