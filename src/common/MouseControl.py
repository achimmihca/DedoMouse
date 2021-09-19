from __future__ import annotations
from typing import Optional
import threading
import time
import pyautogui # type: ignore
from math import sqrt
from enum import Enum
from rx.subject.subject import Subject
import common.AppContext as AppContext
from common.Config import MousePositioningMode
from .LogHolder import LogHolder
from .PidControl import PidControl
from .Vector import Vector
from .util import get_time_ms
from .util import limit_float

# Disable pyautogui delay between actions (https://github.com/asweigart/pyautogui/issues/568)
pyautogui.PAUSE = 0

class MouseControl(LogHolder):
    def __init__(self, app_context: AppContext.AppContext):
        super().__init__()
        self.app_context = app_context
        self.config = app_context.config

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

        self.last_mouse_position: Optional[Vector] = None
        self.mouse_x_pid_control = PidControl(p, i, d)
        self.mouse_y_pid_control = PidControl(p, i, d)
        self.last_mouse_position_time_ms = get_time_ms()
        self.is_drag_started = False
        self.last_single_left_click_time_ms = 0

        self.performed_action_desciption = Subject()

        # Log all performed actions
        self.performed_action_desciption.subscribe(lambda new_value: self.log.info(new_value))

    def on_new_mouse_position_detected(self, new_mouse_px: Vector) -> None:
        if self.config.mouse_positioning_mode.value == MousePositioningMode.RELATIVE:
            self._handle_new_mouse_position_via_relative_positioning(new_mouse_px)
        elif self.config.mouse_positioning_mode.value == MousePositioningMode.ABSOLUTE:
            self._handle_new_mouse_position_via_absolute_positioning(new_mouse_px)

    def _handle_new_mouse_position_via_absolute_positioning(self, new_mouse_px: Vector) -> None:
        if self.config.is_control_mouse_position.value and not self.config.is_all_control_disabled.value:
            delta_time_seconds = (get_time_ms() - self.last_mouse_position_time_ms) / 1000
            current_pos = self._get_mouse_position()
            smooth_mouse_x = self.mouse_x_pid_control.get_next_value(current_pos.x, new_mouse_px.x, delta_time_seconds)
            smooth_mouse_y = self.mouse_y_pid_control.get_next_value(current_pos.y, new_mouse_px.y, delta_time_seconds)
            self._set_mouse_position(Vector(smooth_mouse_x, smooth_mouse_y))
            self.last_mouse_position_time_ms = get_time_ms()

    def _handle_new_mouse_position_via_relative_positioning(self, new_mouse_px: Vector) -> None:
        min_distance_px: float = self.app_context.webcam_control.actual_capture_size.x * self.config.min_mouse_position_difference_percent.value
        if self.config.is_control_mouse_position.value and not self.config.is_all_control_disabled.value:
            if not self.last_mouse_position:
                self.last_mouse_position = new_mouse_px
                return

            mouse_position_difference = new_mouse_px.subtract(self.last_mouse_position)
            if mouse_position_difference.magnitude() <= min_distance_px:
                return
            delta_time_seconds = (get_time_ms() - self.last_mouse_position_time_ms) / 1000

            reduced_mouse_position_difference = mouse_position_difference.scale_by_scalar(1 - self.config.min_mouse_position_difference_percent.value)
            # limit square root to avoid div by zero
            reduced_mouse_position_difference_magniture_square_root = limit_float(sqrt(reduced_mouse_position_difference.magnitude()), 0.000001, None)
            smooth_mouse_difference = (reduced_mouse_position_difference
                                       .scale_by_scalar(1 / reduced_mouse_position_difference_magniture_square_root)
                                       .scale_by_scalar(1 / delta_time_seconds)
                                       .scale_by_scalar(self.config.mouse_position_difference_sensitivity.value))

            current_pos = self._get_mouse_position()
            new_pos = current_pos.add(smooth_mouse_difference)
            self._set_mouse_position(new_pos)
            self.last_mouse_position = new_mouse_px
            self.last_mouse_position_time_ms = get_time_ms()

    def on_single_click_detected(self, mouse_button: MouseButton) -> None:
        if self.is_drag_started:
            self.performed_action_desciption.on_next(f"{mouse_button.name.lower()} click, but ongoing drag")
            return

        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            if mouse_button == MouseButton.LEFT:
                self.last_single_left_click_time_ms = get_time_ms()

            self._do_click(mouse_button)
            self.performed_action_desciption.on_next(f"{mouse_button.name.lower()} click")
        else:
            self.performed_action_desciption.on_next(f"{mouse_button.name.lower()} click, but ignored")

    def on_double_left_click_detected(self) -> None:
        if self.is_drag_started:
            self.performed_action_desciption.on_next("double click, but ongoing drag")
            return

        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            duration_since_last_single_click = get_time_ms() - self.last_single_left_click_time_ms
            if (duration_since_last_single_click < 500):
                # Wait a little bit such that the OS will take the following two clicks as a double click and not as a triple click.
                do_double_click_thread = threading.Thread(target=lambda: self.do_double_click_after_sleep_in_ms(500 - duration_since_last_single_click))
                do_double_click_thread.start()
            else:
                self._do_click(MouseButton.LEFT)
                self._do_click(MouseButton.LEFT)
            self.performed_action_desciption.on_next("double left click")
        else:
            self.performed_action_desciption.on_next("double left click, but ignored")

    def do_double_click_after_sleep_in_ms(self, sleep_time_ms: int) -> None:
        time.sleep(sleep_time_ms / 1000)
        self._do_click(MouseButton.LEFT)
        self._do_click(MouseButton.LEFT)

    def on_begin_drag(self) -> None:
        if self.is_drag_started:
            self.performed_action_desciption.on_next("begin drag but drag already started, thus ignored")
            return

        self.is_drag_started = True
        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            self._do_start_drag()
            self.performed_action_desciption.on_next("begin drag")
        else:
            self.performed_action_desciption.on_next("begin drag, but ignored")

    def on_end_drag(self) -> None:
        if not self.is_drag_started:
            self.performed_action_desciption.on_next("end drag but no drag started yet, thus ignored")
            return

        self.is_drag_started = False
        if self.config.is_control_click.value and not self.config.is_all_control_disabled.value:
            self._do_end_drag()
            self.performed_action_desciption.on_next("end drag")
        else:
            self.performed_action_desciption.on_next("end drag but ignored")

    def on_scroll(self, x: int, y: int) -> None:
        scroll_direction = self._get_scroll_direction(x, y)

        if self.is_drag_started:
            self.performed_action_desciption.on_next(f"scroll {scroll_direction}, but ongoing drag")
            return

        try:
            if self.config.is_control_scroll.value and not self.config.is_all_control_disabled.value:
                self._do_scroll(x, y)
                self.performed_action_desciption.on_next(f"scroll {scroll_direction}")
            else:
                self.performed_action_desciption.on_next(f"scroll {scroll_direction}, but ignored")
        except Exception as e:
            self.performed_action_desciption.on_next(f"scrolling failed (horizontal:{x}, vertical:{y}): {str(e)}")

    def _do_click(self, mouse_button: MouseButton) -> None:
        if mouse_button == MouseButton.LEFT:
            pyautogui.click(button=pyautogui.LEFT)
        if mouse_button == MouseButton.RIGHT:
            pyautogui.click(button=pyautogui.RIGHT)
        if mouse_button == MouseButton.MIDDLE:
            pyautogui.click(button=pyautogui.MIDDLE)

    def _do_start_drag(self) -> None:
        pyautogui.mouseDown(button=pyautogui.LEFT)

    def _do_end_drag(self) -> None:
        pyautogui.mouseUp(button=pyautogui.LEFT)

    def _do_scroll(self, x: int, y: int) -> None:
        if x != 0:
            # Horizontal scrolling not yet supported.
            pass
        if y != 0:
            # Scroll steps are tiny in PyAutoGui. Thus, multiply by some factor.
            pyautogui.scroll(y * self.config.pyautogui_scroll_factor.value)

    def _get_scroll_direction(self, x: int, y: int) -> str:
        if (x > 0 and y == 0):
            return "right"
        if (x < 0 and y == 0):
            return "left"
        if (x == 0 and y > 0):
            return "up"
        if (x == 0 and y < 0):
            return "down"
        return "diagonal"

    def _get_mouse_position(self) -> Vector:
        x, y = pyautogui.position()
        return Vector(x, y)

    def _set_mouse_position(self, new_pos: Vector) -> None:
        pyautogui.moveTo(int(new_pos.x), int(new_pos.y))

class MouseButton(Enum):
    LEFT = 1
    RIGHT = 2
    MIDDLE = 3