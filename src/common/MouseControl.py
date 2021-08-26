from __future__ import annotations
import threading
import time
import mouse # type: ignore
from enum import Enum
from .Config import Config
from .LogHolder import LogHolder
from .PidControl import PidControl
from .Vector import Vector
from .util import get_time_ms

class MouseControl(LogHolder):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

        # Configure PID values:
        # - start by setting i and d to zero and p to a small value.
        # - then configure p, i, d, in this order.

        # Proportional factor between 0 and 1.
        # Increase value if mouse is not moving fast enough to destination.
        # Reduce value if mouse is moving too fast or is jittering.
        p = self.config.mouse_position_pid_p.value

        # Integral factor.
        # Set to 0 if mouse is not moving smoothly. Then slowly increase value until ok.
        i = self.config.mouse_position_pid_i.value

        # Derivative factor.
        # Set to 0 if mouse is not moving smoothly. Then slowly increase value until ok.
        d = self.config.mouse_position_pid_d.value

        self.mouse_x_pid_control = PidControl(p, i, d)
        self.mouse_y_pid_control = PidControl(p, i, d)
        self.last_mouse_position_time_ms = get_time_ms()
        self.is_drag_started = False
        self.last_single_left_click_time_ms = 0

    def on_new_mouse_position_detected(self, new_mouse_px: Vector) -> None:
        if self.config.is_control_mouse_position.value and not self.config.is_all_control_disabled.value:
            delta_time_seconds = (get_time_ms() - self.last_mouse_position_time_ms) / 1000
            current_pos = Vector.from_tuple2(mouse.get_position())
            smooth_mouse_x = self.mouse_x_pid_control.get_next_value(current_pos.x, new_mouse_px.x, delta_time_seconds)
            smooth_mouse_y = self.mouse_y_pid_control.get_next_value(current_pos.y, new_mouse_px.y, delta_time_seconds)
            mouse.move(smooth_mouse_x, smooth_mouse_y)
            self.last_mouse_position_time_ms = get_time_ms()

    def on_single_click_detected(self, mouse_button: MouseButton) -> None:
        if self.is_drag_started:
            self.log.info(f"{mouse_button.name} click, but ongoing drag")
            return

        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            if mouse_button == MouseButton.LEFT:
                self.last_single_left_click_time_ms = get_time_ms()

            self.do_click(mouse_button)
            self.log.info(f"{mouse_button.name} click")
        else:
            self.log.info(f"{mouse_button.name} click, but ignored")

    def on_double_left_click_detected(self) -> None:
        if self.is_drag_started:
            self.log.info("double click, but ongoing drag")
            return

        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            duration_since_last_single_click = get_time_ms() - self.last_single_left_click_time_ms
            if (duration_since_last_single_click < 500):
                # Wait a little bit such that the OS will take the following two clicks as a double click and not as a triple click.
                do_double_click_thread = threading.Thread(target=lambda: self.do_double_click_after_sleep_in_ms(500 - duration_since_last_single_click))
                do_double_click_thread.start()
            else:
                self.do_click(MouseButton.LEFT)
                self.do_click(MouseButton.LEFT)
            self.log.info("double left click")
        else:
            self.log.info("double left click, but ignored")

    def do_double_click_after_sleep_in_ms(self, sleep_time_ms: int) -> None:
        time.sleep(sleep_time_ms / 1000)
        self.do_click(MouseButton.LEFT)
        self.do_click(MouseButton.LEFT)

    def on_begin_drag(self) -> None:
        if self.is_drag_started:
            self.log.info("begin drag but drag already started, thus ignored")
            return

        self.is_drag_started = True
        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            mouse.press(button=mouse.LEFT)
            self.log.info("begin drag")
        else:
            self.log.info("begin drag but ignored")

    def on_end_drag(self) -> None:
        if not self.is_drag_started:
            self.log.info("end drag but no drag started yet, thus ignored")
            return

        self.is_drag_started = False
        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            mouse.release(mouse.LEFT)
            self.log.info("end drag")
        else:
            self.log.info("end drag but ignored")

    def on_scroll(self, x: int, y: int) -> None:
        scroll_direction = self.get_scroll_direction(x, y)

        if self.is_drag_started:
            self.log.info(f"scroll {scroll_direction}, but ongoing drag")
            return

        try:
            if self.config.is_control_scroll.value and not self.config.is_all_control_disabled.value:
                if x != 0:
                    # horizontal scrolling not yet supported by mouse library
                    pass
                if y != 0:
                    mouse.wheel(y)
                self.log.info(f"scroll {scroll_direction}")
            else:
                self.log.info(f"scroll {scroll_direction}, but ignored")
        except Exception as e:
            self.log.error(f"scrolling failed (horizontal:{x}, vertical:{y}): {str(e)}")

    def do_click(self, mouse_button: MouseButton) -> None:
        if mouse_button == MouseButton.LEFT:
            mouse.click(mouse.LEFT)
        if mouse_button == MouseButton.RIGHT:
            mouse.click(mouse.RIGHT)
        if mouse_button == MouseButton.MIDDLE:
            mouse.click(mouse.MIDDLE)

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