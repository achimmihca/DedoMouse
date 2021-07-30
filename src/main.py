import logging
from Config import Config
from Log import initLogging
from MouseControl import MouseControl
from WebcamControl import WebcamControl
from GestureRecognizer import GestureRecognizer
from GlobalShortcutControl import GlobalShortcutControl

initLogging()
logging.getLogger('root').info("=============================================")
logging.getLogger('root').info("DedoMouse started")
logging.getLogger('root').info("=============================================")

config = Config.load_from_file()
config.update_screen_size()

shortcut_control = GlobalShortcutControl(config)
shortcut_control.start_listener()

mouse_control = MouseControl(config)

gesture_regocnizer = GestureRecognizer(config, mouse_control)

webcam_control = WebcamControl(config, gesture_regocnizer)
webcam_control.start_video_capture()

config.save_to_file()

logging.getLogger('root').info("=============================================")
logging.getLogger('root').info("DedoMouse finished")
logging.getLogger('root').info("=============================================")