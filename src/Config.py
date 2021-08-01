from __future__ import annotations
import logging
from os import stat
from typing import Callable, List
from screeninfo import get_monitors # type: ignore
from Vector import Vector
from util import from_json, to_json

class Config:
    config_file_path = "config.json"
    log = logging.getLogger("Config")
    config_change_callbacks: List[Callable] = []

    @staticmethod
    def load_from_file() -> Config:
        try:
            with open(file=Config.config_file_path, mode="r", encoding="utf-8") as file:
                json_string = file.read()
                loaded_config = from_json(json_string, Config)
                loaded_config.running = True

                # Merge with newly created config to ensure all fields are present
                new_config = Config()
                for k,v in new_config.__dict__.items():
                    if not k in loaded_config.__dict__:
                        loaded_config.__dict__[k] = v

                Config.log.info(f"Loaded config from '{Config.config_file_path}'.")
                return loaded_config
        except Exception as e:
            loaded_config = Config()
            Config.log.warning(f"Created new config. Could not load config from '{Config.config_file_path}': {str(e)}")
            return loaded_config

    @staticmethod
    def fire_config_changed_event() -> None:
        for callback in Config.config_change_callbacks:
            callback()

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

        # Mouse position PID values
        self.mouse_position_pid_p = 0.4
        self.mouse_position_pid_i = 0
        self.mouse_position_pid_d = 0.01

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

        self.is_control_mouse_position = False
        self.is_control_click = False
        self.is_control_scroll = False
        self.is_all_control_disabled = False
        self.is_trigger_additional_click_on_double_click = False

        self.is_stay_on_top = False

        self.exit_shortcuts = ["ctrl+shift+alt+esc", "f4"]
        self.toggle_control_mouse_position_shortcuts = ["ctrl+shift+alt+p", "f8"]
        self.toggle_control_click_shortcuts = ["ctrl+shift+alt+c", "f9"]
        self.toggle_control_scroll_shortcuts = ["ctrl+shift+alt+s", "f10"]
        self.toggle_all_control_disabled_shortcuts = ["ctrl+shift+alt+a", "f2"]

    def update_screen_size(self) -> None:
        self.screen_size = Vector(0, 0)

        monitors = get_monitors()

        if len(monitors) <= self.monitor_index:
            Config.log.warning(f"no monitor at index {self.monitor_index}. Using monitor at index 0 instead.")
            self.monitor_index = 0
            self.screen_offset = Vector(0, 0)

        selected_monitor = monitors[self.monitor_index]
        self.screen_size = Vector(selected_monitor.width, selected_monitor.height)

        if self.screen_size.x <= 0 or self.screen_size.y <= 0:
            raise ConfigException("could not determine screen size")

        Config.log.info(f"screen size: {self.screen_size.x} x {self.screen_size.y}")

    def save_to_file(self) -> None:
        json_string = to_json(self, True)
        with open(file=Config.config_file_path, mode="w", encoding="utf-8") as file:
            file.write(json_string)
            Config.log.info(f"Saved config to: {Config.config_file_path}")

class ConfigException(Exception):
    pass