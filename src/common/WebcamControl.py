from __future__ import annotations
from typing import Any, Callable, List, Union
from cv2 import cv2
import numpy as np
import urllib.request
import common.AppContext as AppContext
from common.util import to_json
from .Config import VideoCaptureSource
from .GestureRecognizer import HandFingerPositions
from .LogHolder import LogHolder
from .Vector import Vector
from .draw_util import draw_circle, draw_line
from rx import operators as ops
import rx

class WebcamControl(LogHolder):
    def __init__(self, app_context: AppContext.AppContext):
        super().__init__()
        self.app_context = app_context
        self.config = app_context.config
        self.actual_capture_size = self.config.capture_size.value
        self.fps = self.config.capture_fps.value
        self.gesture_recognizer = app_context.gesture_regocnizer
        self.frame_analyzed_callbacks: List[Callable[[Any, Vector], None]] = []
        self.restart_video_capture_callbacks: List[Callable[[], None]] = []
        self.is_restart_video_capture = False

        # Restart video capture when any video-capture-config has been changed and is stable.
        delay_in_seconds = 3
        self.last_config_json = to_json(self.config, False)
        (rx.of(self.config.capture_device_index.subject,
                  self.config.capture_size.subject,
                  self.config.capture_fps.subject,
                  self.config.capture_source.subject,
                  self.config.capture_source_url.subject)
            .pipe(ops.merge_all())
            .pipe(ops.debounce(delay_in_seconds))
            .subscribe(self.restart_video_capture))

    def restart_video_capture(self, argument: Any = None) -> None:
        current_config_json = to_json(self.config, False)
        if (not self.is_restart_video_capture
                and self.last_config_json != current_config_json):
            self.last_config_json = current_config_json
            self.log.info("init restart of video capture")
            self.is_restart_video_capture = True
            for callback in self.restart_video_capture_callbacks:
                callback()

    def start_video_capture(self) -> Union[str, None]:
        if not self.config.running.value:
            return None

        self.log.info("starting video capture")
        if (self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM
                or not self.config.capture_source_url.value.endswith(".jpg")):
            setup_result = self.start_video_capture_stream()
            if setup_result is not None:
                return setup_result

        pause_in_millis = int(1000 / self.fps)

        self.log.info("starting video capture analysis loop")
        # LOOP START
        self.is_restart_video_capture = False
        while self.config.running.value and (not self.is_restart_video_capture):
            if (self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM
                    or not self.config.capture_source_url.value.endswith(".jpg")):
                ret, frame = self.cap.read()
            else:
                try:
                    img_resp = urllib.request.urlopen(self.config.capture_source_url.value)
                    img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
                    frame = cv2.imdecode(img_np, -1)
                    h, w, c = frame.shape
                    self.actual_capture_size = Vector(w, h)
                except Exception:
                    self.log.exception("Could not access frame from URL")
                    return f"Could not access frame from URL: {self.config.capture_source_url.value}"

            self.process_frame(frame)

            cv2.waitKey(pause_in_millis)
        # LOOP END

        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

        self.log.info("video capture analysis loop finished")

        if self.config.running.value and self.is_restart_video_capture:
            self.log.info("restarting video capture")
            return self.start_video_capture()

        return ""

    def start_video_capture_stream(self) -> Union[str, None]:
        try:
            if (self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM):
                self.cap: Any = cv2.VideoCapture(self.config.capture_device_index.value)
            elif (self.config.capture_source_url.value):
                # Check available video backends
                available_backends = [cv2.videoio_registry.getBackendName(b) for b in cv2.videoio_registry.getBackends()]
                self.log.info(f"available video backends: {available_backends}")

                self.cap = cv2.VideoCapture(self.config.capture_source_url.value)
                self.log.info(f"Video stream of '{self.config.capture_source_url.value}' opened: {self.cap.isOpened()}")
                if (not self.cap.isOpened()):
                    return f"Video stream of '{self.config.capture_source_url.value}' not open"
            else:
                raise Exception("IP Webcam URL not set")
        except Exception as e:
            error_message = f"Failed to start video capture: {str(e)}. Please restart."
            self.log.exception(error_message)
            return error_message

        default_capture_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        default_capture_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.log.info(f"default video capture size of camera: {default_capture_width}x{default_capture_height}")

        # configure video capture
        if self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.capture_size.value.x)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.capture_size.value.y)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.capture_fps.value)

        # check video capture configuration was successful
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.actual_capture_size = Vector(width, height)
        self.config.capture_size.value = self.actual_capture_size
        if (width == 0 or height == 0):
            return "Width or height of video is zero"

        if (self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM
                and (self.config.capture_size.value.x != width
                     or self.config.capture_size.value.y != height)):
            self.log.warning(f"Configured video size {self.config.capture_size.value.x}x{self.config.capture_size.value.y} does not match actual video size {width}x{height}")
            self.config.capture_size.value = self.actual_capture_size

        if (self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM
                and self.config.capture_fps.value != self.fps):
            self.log.warning(f"Configured frames per second {self.config.capture_fps.value} does not match actual frames per second {self.fps}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if (self.fps == 0):
            return "FPS of video is zero"
        if (self.fps > 30):
            self.log.info(f"Unexpected high FPS: {self.fps}. Assuming 30 instead.")
            self.fps = 30
        self.config.capture_fps.value = self.fps

        self.log.info(f"Capturing video (width: {width}, height: {height}, fps: {self.fps})")

        self.gesture_recognizer.actual_capture_size = self.actual_capture_size

        return None

    def process_frame(self, frame: Any) -> None:
        # mirror vertically
        if self.config.capture_flip.value:
            frame = cv2.flip(frame, 1)

        # Convert to RBG Color Space
        if self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Draw some certain configurable values
        self.draw_motion_border_overlay(frame)

        # Analyze image
        hand_finger_positions = self.gesture_recognizer.process_frame(frame)
        if hand_finger_positions:
            self.draw_finger_position_overlay(frame, hand_finger_positions)

        for callback in self.frame_analyzed_callbacks:
            callback(frame, self.actual_capture_size)

    def draw_motion_border_overlay(self, frame: Any) -> None:
        # draw motion border
        color = (127, 127, 127)
        thickness = 2
        motion_border_left_x = self.config.motion_border_left.value * self.actual_capture_size.x
        motion_border_right_x = self.actual_capture_size.x - self.config.motion_border_right.value * self.actual_capture_size.x
        motion_border_top_y = self.config.motion_border_top.value * self.actual_capture_size.y
        motion_border_bottom_y = self.actual_capture_size.y - self.config.motion_border_bottom.value * self.actual_capture_size.y

        # motion border frame
        draw_line(frame, Vector(motion_border_left_x, motion_border_top_y), Vector(motion_border_left_x, motion_border_bottom_y), color, thickness)
        draw_line(frame, Vector(motion_border_right_x, motion_border_top_y), Vector(motion_border_right_x, motion_border_bottom_y), color, thickness)
        draw_line(frame, Vector(motion_border_left_x, motion_border_top_y), Vector(motion_border_right_x, motion_border_top_y), color, thickness)
        draw_line(frame, Vector(motion_border_left_x, motion_border_bottom_y), Vector(motion_border_right_x, motion_border_bottom_y), color, thickness)
        # vertical to edges
        draw_line(frame, Vector(0, 0), Vector(motion_border_left_x, motion_border_top_y), color, thickness)
        draw_line(frame, Vector(self.actual_capture_size.x, 0), Vector(motion_border_right_x, motion_border_top_y), color, thickness)
        draw_line(frame, Vector(0, self.actual_capture_size.y), Vector(motion_border_left_x, motion_border_bottom_y), color, thickness)
        draw_line(frame, Vector(self.actual_capture_size.x, self.actual_capture_size.y), Vector(motion_border_right_x, motion_border_bottom_y), color, thickness)

    def draw_finger_position_overlay(self, frame: Any, hand_finger_positions: HandFingerPositions) -> None:
        # draw landmark positions
        draw_circle(frame, hand_finger_positions.wrist_position.px, 5, (255, 0, 0))
        draw_circle(frame, hand_finger_positions.thumb_tip_position.px, 5, (0, 255, 255))
        draw_circle(frame, hand_finger_positions.index_tip_position.px, 5, (255, 255, 0))
        draw_circle(frame, hand_finger_positions.middle_tip_position.px, 5, (0, 255, 0))
        draw_circle(frame, hand_finger_positions.ring_tip_position.px, 5, (255, 0, 255))
        draw_circle(frame, hand_finger_positions.pinky_tip_position.px, 5, (0, 0, 255))

        # draw click threshold
        draw_circle(frame, hand_finger_positions.thumb_tip_position.px, self.config.click_distance_threshold_low_percent.value * self.actual_capture_size.x / 2, (0, 255, 0), 2)
        draw_circle(frame, hand_finger_positions.thumb_tip_position.px, self.config.click_distance_threshold_high_percent.value * self.actual_capture_size.x / 2, (0, 255, 0), 2)
