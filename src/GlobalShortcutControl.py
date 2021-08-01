import keyboard # type: ignore
from Config import Config
from Gui import MainQtWindow
from LogHolder import LogHolder

class GlobalShortcutControl(LogHolder):
    def __init__(self, config: Config, main_gui: MainQtWindow):
        super().__init__()
        self.config = config
        self.main_gui = main_gui
 
    def start_listener(self) -> None:
        for shortcut in self.config.exit_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_exit, args=[shortcut])
        for shortcut in self.config.toggle_control_mouse_position_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_mouse_position)
        for shortcut in self.config.toggle_control_click_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_click)
        for shortcut in self.config.toggle_control_scroll_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_toggle_control_scroll)
        for shortcut in self.config.toggle_all_control_disabled_shortcuts:
            keyboard.add_hotkey(shortcut, self.on_toggle_all_control_disabled)

    def on_exit(self, shortcut: str) -> None:
        self.log.info(f'Closing app because of shortcut: {shortcut}')
        self.main_gui.close()

    def on_toggle_control_mouse_position(self) -> None:
        self.config.is_control_mouse_position = not self.config.is_control_mouse_position
        self.log.info(f"Control mouse position: {self.config.is_control_mouse_position}")
        Config.fire_config_changed_event()

    def on_toggle_control_click(self) -> None:
        self.config.is_control_click = not self.config.is_control_click
        self.log.info(f"Control click: {self.config.is_control_click}")
        Config.fire_config_changed_event()

    def on_toggle_control_scroll(self) -> None:
        self.config.is_control_scroll = not self.config.is_control_scroll
        self.log.info(f"Control scroll: {self.config.is_control_scroll}")
        Config.fire_config_changed_event()
    
    def on_toggle_all_control_disabled(self) -> None:
        self.config.is_all_control_disabled = not self.config.is_all_control_disabled
        self.log.info(f"Control all disabled: {self.config.is_all_control_disabled}")
        Config.fire_config_changed_event()