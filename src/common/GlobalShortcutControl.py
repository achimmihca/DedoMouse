from __future__ import annotations
import keyboard # type: ignore
import common.AppContext as AppContext
from .LogHolder import LogHolder

class GlobalShortcutControl(LogHolder):
    def __init__(self, app_context: AppContext.AppContext):
        super().__init__()
        self.app_context = app_context
        self.config = app_context.config
        self.on_close_callback = app_context.main_window.close
 
    def start_listener(self) -> None:
        try:
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
        except Exception:
            self.log.exception("Could not register shortcuts")

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
