from typing import Callable
import keyboard # type: ignore
from .Config import Config
from .LogHolder import LogHolder

class GlobalShortcutControl(LogHolder):
    def __init__(self, config: Config, on_close_callback: Callable):
        super().__init__()
        self.config = config
        self.on_close_callback = on_close_callback
 
    def start_listener(self) -> None:
        for shortcut in self.config.exit_shortcuts.value:
            keyboard.add_hotkey(shortcut, self.on_exit, args=[shortcut])
        for shortcut in self.config.toggle_control_mouse_position_shortcuts.value:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_mouse_position)
        for shortcut in self.config.toggle_control_click_shortcuts.value:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_click)
        for shortcut in self.config.toggle_control_scroll_shortcuts.value:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_scroll)
        for shortcut in self.config.toggle_all_control_disabled_shortcuts.value:
            keyboard.add_hotkey(shortcut, self.on_toggle_all_control_disabled)

    def on_exit(self, shortcut: str) -> None:
        self.log.info(f'Closing app because of shortcut: {shortcut}')
        self.on_close_callback()

    def on_toggle_control_mouse_position(self) -> None:
        self.config.is_control_mouse_position.value = not self.config.is_control_mouse_position.value

    def on_toggle_control_click(self) -> None:
        self.config.is_control_click.value = not self.config.is_control_click.value

    def on_toggle_control_scroll(self) -> None:
        self.config.is_control_scroll.value = not self.config.is_control_scroll.value

    def on_toggle_all_control_disabled(self) -> None:
        self.config.is_all_control_disabled.value = not self.config.is_all_control_disabled.value
        self.log.info(f"Control all disabled: {self.config.is_all_control_disabled.value}")
