from pynput.mouse import Button, Controller
from Config import Config

class MouseControl:
    def __init__(self, config: Config):
        self.config = config
        self.mouse_controller = Controller()

    def on_new_mouse_position_detected(self, new_mouse_x, new_mouse_y):
        if self.config.is_control_mouse_position:
            self.mouse_controller.position = (new_mouse_x, new_mouse_y)

    def on_click_detected(self):
        if self.config.is_control_click:
            self.mouse_controller.click(Button.left, 1)
            print("left click")
        else:
            print("left click, but ignored")