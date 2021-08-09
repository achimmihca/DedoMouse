from typing import Any, Callable, List
from cv2 import cv2
import mediapipe as mp # type: ignore
from .Config import Config
from .GestureRecognizer import GestureRecognizer, HandFingerPositions
from .LogHolder import LogHolder
from .Vector import Vector
from .draw_util import draw_circle, draw_line

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
            # Convert to RBG Color Space
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Draw some certain configurable values
            self.draw_motion_border_overlay(frame)

            # Analyze image
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
                hand_finger_positions = self.gesture_regocnizer.process_hand_landmarks(frame, results.multi_hand_landmarks)

                # Draw finger positions overlay
                self.draw_finger_position_overlay(frame, hand_finger_positions)

            for callback in self.frame_analyzed_callbacks:
                callback(frame)

            cv2.waitKey(33)

        cap.release()
        cv2.destroyAllWindows()

        self.log.info("video capture analysis loop finished")

    def draw_motion_border_overlay(self, frame: Any) -> None:
        # draw motion border
        color = (127, 127, 127)
        thickness = 2
        motion_border_left_x = self.config.motion_border_left.value * self.config.capture_size.value.x
        motion_border_right_x = self.config.capture_size.value.x - self.config.motion_border_right.value * self.config.capture_size.value.x
        motion_border_top_y = self.config.motion_border_top.value * self.config.capture_size.value.y
        motion_border_bottom_y = self.config.capture_size.value.y - self.config.motion_border_bottom.value * self.config.capture_size.value.y

        # motion border frame
        draw_line(frame, Vector(motion_border_left_x, motion_border_top_y), Vector(motion_border_left_x, motion_border_bottom_y), color, thickness)
        draw_line(frame, Vector(motion_border_right_x, motion_border_top_y), Vector(motion_border_right_x, motion_border_bottom_y), color, thickness)
        draw_line(frame, Vector(motion_border_left_x, motion_border_top_y), Vector(motion_border_right_x, motion_border_top_y), color, thickness)
        draw_line(frame, Vector(motion_border_left_x, motion_border_bottom_y), Vector(motion_border_right_x, motion_border_bottom_y), color, thickness)
        # vertical to edges
        draw_line(frame, Vector(0, 0), Vector(motion_border_left_x, motion_border_top_y), color, thickness)
        draw_line(frame, Vector(self.config.capture_size.value.x, 0), Vector(motion_border_right_x, motion_border_top_y), color, thickness)
        draw_line(frame, Vector(0, self.config.capture_size.value.y), Vector(motion_border_left_x, motion_border_bottom_y), color, thickness)
        draw_line(frame, Vector(self.config.capture_size.value.x, self.config.capture_size.value.y), Vector(motion_border_right_x, motion_border_bottom_y), color, thickness)

    def draw_finger_position_overlay(self, frame: Any, hand_finger_positions: HandFingerPositions) -> None:
        # draw landmark positions
        draw_circle(frame, hand_finger_positions.wrist_position.px, 5, (255, 0, 0))
        draw_circle(frame, hand_finger_positions.thumb_tip_position.px, 5, (0, 255, 255))
        draw_circle(frame, hand_finger_positions.index_tip_position.px, 5, (255, 255, 0))
        draw_circle(frame, hand_finger_positions.middle_tip_position.px, 5, (0, 255, 0))

        # draw click threshold
        draw_circle(frame, hand_finger_positions.thumb_tip_position.px, self.config.click_distance_threshold_low_percent.value * self.config.capture_size.value.x / 2, (0, 255, 0), 2)
        draw_circle(frame, hand_finger_positions.thumb_tip_position.px, self.config.click_distance_threshold_high_percent.value * self.config.capture_size.value.x / 2, (0, 255, 0), 2)
