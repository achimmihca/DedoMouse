from screeninfo import get_monitors

class Config:
    def __init__(self):
        self.running = True
        self.use_webcam = True
        
        self.screen_width = 768
        self.screen_height = 1280
        
        self.capture_width = 640
        self.capture_height = 480
        # Motion does not (cannot) use the full capture range
        self.motion_border_left = self.capture_width * 0.15
        self.motion_border_right = self.capture_width * 0.15
        self.motion_border_top = self.capture_height * 0.4
        self.motion_border_bottom = self.capture_height * 0.15

        self.click_distance_threshold = 20
        self.click_delay_ms = 300

        self.damping_factor = 2
        self.is_control_mouse_position = False
        self.is_control_click = False

    def update_screen_size(self):
        self.screen_width = 0
        self.screen_height = 0
        for monitor in get_monitors():
            # assume horizontal alignment of monitors in landscape orientation
            self.screen_width += monitor.width
            self.screen_height = max(self.screen_height, monitor.height)

        if self.screen_width <= 0 or self.screen_height <= 0:
            raise "could not determine screen size"

        print(f"screen size: {self.screen_width} x {self.screen_height}")