from typing import Any
from pynput import keyboard # type: ignore
from Config import Config
from LogHolder import LogHolder

class GlobalShortcutControl(LogHolder):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def start_listener(self) -> None:
        keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_pressed)
        # start to listen on a separate thread
        keyboard_listener.start()  

    def on_keyboard_pressed(self, key: Any) -> bool:
        key_name = self.get_key_name(key)
        self.log.debug(f'key pressed {key_name}')
        
        if key_name in self.config.exit_keys:
            self.log.info(f'on_keyboard_pressed - stopping main loop because of key press: {key_name}')
            self.config.running = False
            # stop listener by returning False
            return False

        if key_name in self.config.toggle_control_mouse_position_keys:
            self.config.is_control_mouse_position = not self.config.is_control_mouse_position
            self.log.info(f"Control mouse position: {self.config.is_control_mouse_position}")

        if key_name in self.config.toggle_control_click_keys:
            self.config.is_control_click = not self.config.is_control_click
            self.log.info(f"Control click: {self.config.is_control_click}")

        if key_name in self.config.toggle_control_scroll_keys:
            self.config.is_control_scroll = not self.config.is_control_scroll
            self.log.info(f"Control scroll: {self.config.is_control_scroll}")

        return True

    def get_key_name(self, key: Any) -> str:
        try:
            # single-char keys
            return key.char # type: ignore
        except:
            # other keys
            return key.name # type: ignore