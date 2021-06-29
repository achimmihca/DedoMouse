from pynput.mouse import Button, Controller
from Config import Config
from PidControl import PidControl
from util import get_time_ms

class MouseControl:
    def __init__(self, config: Config):
        self.config = config
        self.mouse_controller = Controller()

        # Configure PID values:
        # - start by setting i and d to zero and p to a small value.
        # - then configure p, i, d, in this order.

        # Proportional factor between 0 and 1.
        # Increase value if mouse is not moving fast enough to destination.
        # Reduce value if mouse is moving too fast or is jittering.
        p = 0.4

        # Integral factor.
        # Set to 0 if mouse is not moving smoothly. Then slowly increase value until ok.
        i = 0
        
        # Derivative factor.
        # Set to 0 if mouse is not moving smoothly. Then slowly increase value until ok.
        d = 0.01
        
        self.mouse_x_pid_control = PidControl(p, i, d)
        self.mouse_y_pid_control = PidControl(p, i, d)
        self.last_mouse_position_time_ms = get_time_ms()

    def on_new_mouse_position_detected(self, new_mouse_x, new_mouse_y):
        if self.config.is_control_mouse_position:
            delta_time_seconds = (get_time_ms() - self.last_mouse_position_time_ms) / 1000
            current_x = self.mouse_controller.position[0]
            current_y = self.mouse_controller.position[1]
            smooth_mouse_x = self.mouse_x_pid_control.get_next_value(current_x, new_mouse_x, delta_time_seconds)
            smooth_mouse_y = self.mouse_y_pid_control.get_next_value(current_y, new_mouse_y, delta_time_seconds)
            self.mouse_controller.position = (smooth_mouse_x, smooth_mouse_y)
            self.last_mouse_position_time_ms = get_time_ms()

    def on_click_detected(self):
        if self.config.is_control_click:
            self.mouse_controller.click(Button.left, 1)
            print("left click")
        else:
            print("left click, but ignored")
