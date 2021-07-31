import keyboard # type: ignore
from Config import Config
from LogHolder import LogHolder

class GlobalShortcutControl(LogHolder):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
 
    def start_listener(self) -> None:
        for shortcut in self.config.exit_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_exit, args=[shortcut])
        for shortcut in self.config.toggle_control_mouse_position_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_mouse_position)
        for shortcut in self.config.toggle_control_click_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_click)
        for shortcut in self.config.toggle_control_scroll_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_scroll)

    def on_exit(self, shortcut: str) -> None:
        self.log.info(f'Stopping main loop because of shortcut: {shortcut}')
        self.config.running = False

    def on_toggle_control_mouse_position(self) -> None:
        self.config.is_control_mouse_position = not self.config.is_control_mouse_position
        self.log.info(f"Control mouse position: {self.config.is_control_mouse_position}")

    def on_toggle_control_click(self) -> None:
        self.config.is_control_click = not self.config.is_control_click
        self.log.info(f"Control click: {self.config.is_control_click}")

    def on_toggle_control_scroll(self) -> None:
        self.config.is_control_scroll = not self.config.is_control_scroll
        self.log.info(f"Control scroll: {self.config.is_control_scroll}")