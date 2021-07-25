from screeninfo import get_monitors # type: ignore

from Vector import Vector

class Config:
    def __init__(self) -> None:
        self.running = True
        self.use_webcam = True
        
        self.monitor_index = 1

        self.screen_size = Vector(1280, 720)
        self.screen_offset = Vector(0, 0)
        self.capture_size = Vector(1280, 720)
        self.capture_fps = 5
        # Motion does not (cannot) use the full capture range
        self.motion_border_left = 0.15
        self.motion_border_right = 0.15
        self.motion_border_top = 0.3
        self.motion_border_bottom = 0.15

        # Distance percent of capture_size
        self.click_distance_threshold_low_percent = 0.06
        self.click_distance_threshold_high_percent = self.click_distance_threshold_low_percent * 1.5
        # Min time between two single click gestures.
        self.single_click_delay_ms = 600
        # Max time between two single click gestures for triggering a double click.
        # A double click is fired when two click gestures are detected with less time between them.
        self.double_click_delay_ms = 400
        # A drag gesture is started when a click is held for at least this duration.
        self.drag_start_click_time_ms = 1000

        self.damping_factor = 2
        self.is_control_mouse_position = False
        self.is_control_click = False

    def update_screen_size(self) -> None:
        self.screen_size = Vector(0, 0)

        monitors = get_monitors()
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

        print(f"screen size: {self.screen_size.x} x {self.screen_size.y}")

class ConfigException(Exception):
    pass