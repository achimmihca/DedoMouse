from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from common.Config import Config
from common.ConfigJsonHandler import ConfigJsonHandler
from gui.MainWindow import MainWindow
from common.MouseControl import MouseControl
from common.WebcamControl import WebcamControl
from common.GestureRecognizer import GestureRecognizer
from common.GlobalShortcutControl import GlobalShortcutControl

class AppContext:
    def __init__(self) -> None:
        # Load config from file
        self.config = Config.load_from_file()
        if self.config.screen_size.value.x <= 0 or self.config.screen_size.value.y <= 0:
            self.config.update_screen_size()

        # Log when a value changes
        self.config.enable_logging_on_value_change()

        # Create relevant class instances
        self.mouse_control = MouseControl(self)
        self.gesture_regocnizer = GestureRecognizer(self)
        self.webcam_control = WebcamControl(self)

        # Create Qt Application
        self.qt_application = QApplication(sys.argv)
        apply_stylesheet(self.qt_application, theme=self.config.ui_theme.value)
        self.config.ui_theme.subscribe(lambda new_theme: apply_stylesheet(self.qt_application, theme=new_theme))

        self.main_window = MainWindow(self.config, self.webcam_control)

        # Register global shortcut control
        shortcut_control = GlobalShortcutControl(self)
        shortcut_control.start_listener()

        self.main_window.show()
        sys.exit(self.qt_application.exec())

    @staticmethod
    def configure_json_handlers() -> None:
        ConfigJsonHandler.handles(Config)