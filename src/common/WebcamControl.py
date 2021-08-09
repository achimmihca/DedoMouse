from typing import Any, Callable, List
from cv2 import cv2
import mediapipe as mp # type: ignore
from .Config import Config
from .GestureRecognizer import GestureRecognizer
from .LogHolder import LogHolder
from .Vector import Vector

class WebcamControl(LogHolder):
    def __init__(self, config: Config, gesture_regocnizer: GestureRecognizer):
        super().__init__()
        self.config = config
        self.gesture_regocnizer = gesture_regocnizer
        self.fps = 0
        self.frame_analyzed_callbacks: List[Callable] = []

    def start_video_capture(self) -> None:
        if not self.config.running.value:
            return

        self.log.info("starting video capture")
        cap = cv2.VideoCapture(0)

        # configure video capture
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.capture_size.value.x)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.capture_size.value.y)
        cap.set(cv2.CAP_PROP_FPS, self.config.capture_fps.value)

        # check video capture configuration was successful
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if (self.config.capture_size.value.x != width
                or self.config.capture_size.value.y != height):
            self.log.warning(f"Configured video size {self.config.capture_size.value.x}x{self.config.capture_size.value.y} does not match actual video size {width}x{height}")
            self.config.capture_size.value = Vector(width, height)

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        if (self.config.capture_fps.value != self.fps):
            self.log.warning(f"Configured frames per second {self.config.capture_fps.value} does not match actual frames per second {self.fps}")

        self.log.info(f"Capturing video (width: {width}, height: {height}, fps: {self.fps})")

        hands = mp.solutions.hands.Hands(max_num_hands=1)

        self.log.info("starting video capture analysis loop")
        while self.config.running.value:
            ret, frame = cap.read()
            
            # mirror vertically
            frame = cv2.flip(frame, 1)
            
            # analyze image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                self.gesture_regocnizer.process_hand_landmarks(frame, results.multi_hand_landmarks)

            # draw overlay
            self.draw_overlay(frame)

            for callback in self.frame_analyzed_callbacks:
                callback(frame)

            cv2.waitKey(33)

        cap.release()
        cv2.destroyAllWindows()

        self.log.info("video capture analysis loop finished")

    def draw_overlay(self, frame: Any) -> None:
        pass