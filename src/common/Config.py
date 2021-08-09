from __future__ import annotations
import logging
from screeninfo import get_monitors
from .Vector import Vector
from .util import from_json, to_json
from .ReactiveProperty import ReactiveProperty

class Config:
    config_file_path = "config.json"
    log = logging.getLogger("Config")

    @staticmethod
    def load_from_file() -> Config:
        try:
            with open(file=Config.config_file_path, mode="r", encoding="utf-8") as file:
                json_string = file.read()
                loaded_config = from_json(json_string, Config)
                loaded_config.running.value = True
                Config.log.info(f"Loaded config from '{Config.config_file_path}'.")
                return loaded_config
        except Exception as e:
            loaded_config = Config()
            Config.log.error(f"Created new config. Could not load config from '{Config.config_file_path}'")
            Config.log.exception(e)
            return loaded_config

    def __init__(self) -> None:
        self.running = ReactiveProperty(True)
        self.use_webcam = ReactiveProperty(True)
        
        self.monitor_index = ReactiveProperty(1)

        self.screen_size = ReactiveProperty(Vector(1280, 720))
        self.screen_offset = ReactiveProperty(Vector(0, 0))
        self.capture_size = ReactiveProperty(Vector(1280, 720))
        self.capture_fps = ReactiveProperty(30)
        # Motion does not (cannot) use the full capture range
        self.motion_border_left = ReactiveProperty(0.15)
        self.motion_border_right = ReactiveProperty(0.15)
        self.motion_border_top = ReactiveProperty(0.3)
        self.motion_border_bottom = ReactiveProperty(0.15)

        # Mouse position PID values
        self.mouse_position_pid_p = ReactiveProperty(0.4)
        self.mouse_position_pid_i = ReactiveProperty(0)
        self.mouse_position_pid_d = ReactiveProperty(0.01)

        # Distance percent of capture_size.
        self.click_distance_threshold_low_percent = ReactiveProperty(0.06)
        self.click_distance_threshold_high_percent = ReactiveProperty(self.click_distance_threshold_low_percent.value * 1.5)
        # Min time between two single click gestures.
        self.single_click_pause_ms = ReactiveProperty(600)
        # Max time between two single click gestures for triggering a double click.
        # A double click is fired when two click gestures are detected with less time between them.
        self.double_click_max_pause_ms = ReactiveProperty(400)
        # Wait time before changing to continued scroll mode.
        self.continued_scroll_mode_delay_ms = ReactiveProperty(1200)
        # Min time between two scroll events in continued scroll mode.
        self.continued_scroll_pause_ms = ReactiveProperty(100)
        # A drag gesture is started when a click is held for at least this duration.
        self.drag_start_click_delay_ms = ReactiveProperty(1000)

        self.is_control_mouse_position = ReactiveProperty(False)
        self.is_control_click = ReactiveProperty(False)
        self.is_control_scroll = ReactiveProperty(False)
        self.is_all_control_disabled = ReactiveProperty(False)
        self.is_trigger_additional_click_on_double_click = ReactiveProperty(False)

        self.is_stay_on_top = ReactiveProperty(False)

        self.exit_shortcuts = ReactiveProperty(["ctrl+shift+alt+esc", "f4"])
        self.toggle_control_mouse_position_shortcuts = ReactiveProperty(["ctrl+shift+alt+p", "f8"])
        self.toggle_control_click_shortcuts = ReactiveProperty(["ctrl+shift+alt+c", "f9"])
        self.toggle_control_scroll_shortcuts = ReactiveProperty(["ctrl+shift+alt+s", "f10"])
        self.toggle_all_control_disabled_shortcuts = ReactiveProperty(["ctrl+shift+alt+a", "f2"])

    def enable_logging_on_value_change(self) -> None:
        for k, v in self.__dict__.items():
            if (isinstance(v, ReactiveProperty)):
                v.subscribe(lambda new_value: self.log.info(f"config changed: {k}: {new_value}"))

    def update_screen_size(self) -> None:
        self.screen_size.value = Vector(0, 0)

        monitors = get_monitors()

        if len(monitors) <= self.monitor_index.value:
            Config.log.warning(f"no monitor at index {self.monitor_index}. Using monitor at index 0 instead.")
            self.monitor_index.value = 0
            self.screen_offset.value = Vector(0, 0)

        selected_monitor = monitors[self.monitor_index.value]
        self.screen_size.value = Vector(selected_monitor.width, selected_monitor.height)

        if self.screen_size.value.x <= 0 or self.screen_size.value.y <= 0:
            raise ConfigException("could not determine screen size")

        Config.log.info(f"screen size: {self.screen_size.value.x} x {self.screen_size.value.y}")

    def save_to_file(self) -> None:
        json_string = to_json(self, True)
        with open(file=Config.config_file_path, mode="w", encoding="utf-8") as file:
            file.write(json_string)
            Config.log.info(f"Saved config to: {Config.config_file_path}")


class ConfigException(Exception):
    pass
