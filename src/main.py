from Config import Config
from MouseControl import MouseControl
from WebcamControl import WebcamControl
from GestureRecognizer import GestureRecognizer
from GlobalShortcutControl import GlobalShortcutControl

config = Config()
config.update_screen_size()

shortcut_control = GlobalShortcutControl(config)
shortcut_control.start_listener()

mouse_control = MouseControl(config)

gesture_regocnizer = GestureRecognizer(config, mouse_control)

webcam_control = WebcamControl(config, gesture_regocnizer)
webcam_control.start_video_capture()