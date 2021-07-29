from __future__ import annotations
from pynput import keyboard # type: ignore
from screeninfo import get_monitors # type: ignore
from LogHolder import LogHolder

from Vector import Vector

class Config(LogHolder):
    def __init__(self) -> None:
        super().__init__()
        self.running = True
        self.use_webcam = True
        
        self.monitor_index = 1

        self.screen_size = Vector(1280, 720)
        self.screen_offset = Vector(0, 0)
        self.capture_size = Vector(1280, 720)
        self.capture_fps = 30
        # Motion does not (cannot) use the full capture range
        self.motion_border_left = 0.15
        self.motion_border_right = 0.15
        self.motion_border_top = 0.3
        self.motion_border_bottom = 0.15

        # Distance percent of capture_size.
        self.click_distance_threshold_low_percent = 0.06
        self.click_distance_threshold_high_percent = self.click_distance_threshold_low_percent * 1.5
        # Min time between two single click gestures.
        self.single_click_pause_ms = 600
        # Max time between two single click gestures for triggering a double click.
        # A double click is fired when two click gestures are detected with less time between them.
        self.double_click_max_pause_ms = 400
        # Wait time before changing to continued scroll mode.
        self.continued_scroll_mode_delay_ms = 1200
        # Min time between two scroll events in continued scroll mode.
        self.continued_scroll_pause_ms = 100
        # A drag gesture is started when a click is held for at least this duration.
        self.drag_start_click_delay_ms = 1000

        self.damping_factor = 2
        self.is_control_mouse_position = False
        self.is_control_click = False
        self.is_control_scroll = False

        self.exit_keys = [keyboard.Key.esc, keyboard.Key.f4]
        self.toggle_control_mouse_position_keys = [keyboard.Key.f9]
        self.toggle_control_click_keys = [keyboard.Key.f10]
        self.toggle_control_scroll_keys = [keyboard.Key.f8]

    def update_screen_size(self) -> None:
        self.screen_size = Vector(0, 0)

        monitors = get_monitors()

        if len(monitors) <= self.monitor_index:
            self.log.warning(f"no monitor at index {self.monitor_index}. Using monitor at index 0 instead.")
            self.monitor_index = 0

        selected_monitor = monitors[self.monitor_index]
        self.screen_size = Vector(selected_monitor.width, selected_monitor.height)

        # Assume selected monitor is right of others monitor
        if self.monitor_index > 0:
            other_monitors = [m for m in monitors if m != selected_monitor]
            for other_monitor in other_monitors:
                new_offset_x = max(self.screen_offset.x, other_monitor.width)
                self.screen_offset = Vector(new_offset_x, self.screen_offset.y)

        if self.screen_size.x <= 0 or self.screen_size.y <= 0:
            raise ConfigException("could not determine screen size")

        self.log.info(f"screen size: {self.screen_size.x} x {self.screen_size.y}")

class ConfigException(Exception):
    pass