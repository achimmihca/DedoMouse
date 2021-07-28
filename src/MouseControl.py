from __future__ import annotations
from enum import Enum
from typing import Any
from pynput.mouse import Button, Controller  # type: ignore
from Config import Config
from PidControl import PidControl
from Vector import Vector
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
        self.is_drag_started = False

    def on_new_mouse_position_detected(self, new_mouse_px: Vector) -> None:
        if self.config.is_control_mouse_position:
            delta_time_seconds = (get_time_ms() - self.last_mouse_position_time_ms) / 1000
            current_pos = Vector.from_tuple2(self.mouse_controller.position)
            smooth_mouse_x = self.mouse_x_pid_control.get_next_value(current_pos.x, new_mouse_px.x, delta_time_seconds)
            smooth_mouse_y = self.mouse_y_pid_control.get_next_value(current_pos.y, new_mouse_px.y, delta_time_seconds)
            self.mouse_controller.position = (smooth_mouse_x, smooth_mouse_y)
            self.last_mouse_position_time_ms = get_time_ms()

    def on_single_click_detected(self, mouse_button: MouseButton) -> None:
        mouse_button_name = mouse_button.get_name()
        if self.is_drag_started:
            print(f"{mouse_button_name} click, but ongoing drag")
            return

        if self.config.is_control_click:
            self.mouse_controller.click(mouse_button.get_pynput_value(), 1)
            print(f"{mouse_button_name} click")
        else:
            print(f"{mouse_button_name} click, but ignored")

    def on_double_left_click_detected(self) -> None:
        if self.is_drag_started:
            print("double click, but ongoing drag")
            return

        if self.config.is_control_click:
            self.mouse_controller.click(Button.left, 1)
            self.mouse_controller.click(Button.left, 1)
            print("double left click")
        else:
            print("double left click, but ignored")

    def on_begin_drag(self) -> None:
        if self.is_drag_started:
            print("begin drag but drag already started, thus ignored")
            return

        self.is_drag_started = True
        if self.config.is_control_click:
            self.mouse_controller.press(Button.left)
            print("begin drag")
        else:
            print("begin drag but ignored")

    def on_end_drag(self) -> None:
        if not self.is_drag_started:
            print("end drag but no drag started yet, thus ignored")
            return

        self.is_drag_started = False
        if self.config.is_control_click:
            self.mouse_controller.release(Button.left)
            print("end drag")
        else:
            print("end drag but ignored")

    def on_scroll(self, x: int, y: int) -> None:
        scroll_direction = self.get_scroll_direction(x, y)

        if self.is_drag_started:
            print(f"scroll {scroll_direction}, but ongoing drag")
            return

        if self.config.is_control_scroll:
            self.mouse_controller.scroll(x, y)
            print(f"scroll {scroll_direction}")
        else:
            print(f"scroll {scroll_direction}, but ignored")

    def get_scroll_direction(self, x: int, y: int) -> str:
        if (x > 0 and y == 0):
            return "right"
        if (x < 0 and y == 0):
            return "left"
        if (x == 0 and y > 0):
            return "up"
        if (x == 0 and y < 0):
            return "down"
        return "diagonal"

class MouseButton(Enum):
    LEFT = 1
    RIGHT = 2
    MIDDLE = 3

    def get_name(self) -> str:
        if self == MouseButton.LEFT:
            return "left"
        if self == MouseButton.RIGHT:
            return "right"
        if self == MouseButton.MIDDLE:
            return "middle"
        raise Exception(f"Unkown mouse button {self}")

    def get_pynput_value(self) -> Any:
        if self == MouseButton.LEFT:
            return Button.left
        if self == MouseButton.RIGHT:
            return Button.right
        if self == MouseButton.MIDDLE:
            return Button.middle
        raise Exception(f"Unkown mouse button {self}")