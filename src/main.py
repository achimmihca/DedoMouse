from __future__ import annotations
import logging
import sys

from PySide6.QtWidgets import QApplication
from Config import Config
from ConfigJsonHandler import ConfigJsonHandler
from gui.MainWindow import MainWindow
from Log import init_logging
from MouseControl import MouseControl
from WebcamControl import WebcamControl
from GestureRecognizer import GestureRecognizer
from GlobalShortcutControl import GlobalShortcutControl

init_logging()
logging.getLogger('root').info("=============================================")
logging.getLogger('root').info("DedoMouse started")
logging.getLogger('root').info("=============================================")

ConfigJsonHandler.handles(Config)
config = Config.load_from_file()

config.update_screen_size()

mouse_control = MouseControl(config)

gesture_regocnizer = GestureRecognizer(config, mouse_control)

webcam_control = WebcamControl(config, gesture_regocnizer)

app = QApplication(sys.argv)
win = MainWindow(config, webcam_control)

shortcut_control = GlobalShortcutControl(config, win.close)
shortcut_control.start_listener()

win.show()
sys.exit(app.exec())