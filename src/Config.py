from screeninfo import get_monitors # type: ignore

class Config:
    def __init__(self) -> None:
        self.running = True
        self.use_webcam = True
        
        self.monitor_index = 1

        self.screen_width = 1280
        self.screen_height = 720
        
        self.screen_offset_x = 0
        self.screen_offset_y = 0

        self.capture_width = 1280
        self.capture_height = 720
        self.capture_fps = 5
        # Motion does not (cannot) use the full capture range
        self.motion_border_left = self.capture_width * 0.15
        self.motion_border_right = self.capture_width * 0.15
        self.motion_border_top = self.capture_height * 0.3
        self.motion_border_bottom = self.capture_height * 0.15

        self.click_distance_threshold = 20
        self.click_delay_ms = 300

        self.damping_factor = 2
        self.is_control_mouse_position = False
        self.is_control_click = False

    def update_screen_size(self) -> None:
        self.screen_width = 0
        self.screen_height = 0

        monitors = get_monitors()
        selected_monitor = monitors[self.monitor_index]
        self.screen_width = selected_monitor.width
        self.screen_height = selected_monitor.height

        # assume selected monitor is right of others monitor
        if self.monitor_index > 0:
            other_monitors = [m for m in monitors if m != selected_monitor]
            for other_monitor in other_monitors:
                self.screen_offset_x = max(self.screen_offset_x, other_monitor.width)

        if self.screen_width <= 0 or self.screen_height <= 0:
            raise ConfigException("could not determine screen size")

        print(f"screen size: {self.screen_width} x {self.screen_height}")

class ConfigException(Exception):
    pass