from __future__ import annotations
import logging
import sys

from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from common.Config import Config
from common.ConfigJsonHandler import ConfigJsonHandler
from gui.MainWindow import MainWindow
from common.Log import init_logging
from common.MouseControl import MouseControl
from common.WebcamControl import WebcamControl
from common.GestureRecognizer import GestureRecognizer
from common.GlobalShortcutControl import GlobalShortcutControl
from common.version import version
init_logging()
logging.getLogger('root').info("=============================================")
logging.getLogger('root').info(f"DedoMouse {version} started")
logging.getLogger('root').info("=============================================")

ConfigJsonHandler.handles(Config)
config = Config.load_from_file()
if config.screen_size.value.x <= 0 or config.screen_size.value.y <= 0:
    config.update_screen_size()
config.enable_logging_on_value_change()

mouse_control = MouseControl(config)

gesture_regocnizer = GestureRecognizer(config, mouse_control)

webcam_control = WebcamControl(config, gesture_regocnizer)

app = QApplication(sys.argv)
apply_stylesheet(app, theme=config.ui_theme.value)
config.ui_theme.subscribe(lambda new_theme: apply_stylesheet(app, theme=new_theme))

win = MainWindow(config, webcam_control)

shortcut_control = GlobalShortcutControl(config, win.close)
shortcut_control.start_listener()

win.show()
sys.exit(app.exec())