from math import sqrt
from typing import Any
from cv2 import cv2 # type: ignore
from util import get_time_ms
from MouseControl import MouseControl
from Config import Config
from Vector import Vector

class GestureRecognizer:
    def __init__(self, config: Config, mouse_control: MouseControl):
        self.config = config
        self.mouse_control = mouse_control
        self.last_click_time_ms = 0

    def process_hand_landmarks(self, frame: Any, multi_hand_landmarks: Any) -> None:
        if (len(multi_hand_landmarks) <= 0):
            return

        # find landmark positions
        try:
            first_hand_landmarks = multi_hand_landmarks[0]
            wrist_pos_percent = Vector.from_xy(first_hand_landmarks.landmark[0])
            thumb_pos_percent = Vector.from_xy(first_hand_landmarks.landmark[4])
            index_pos_percent = Vector.from_xy(first_hand_landmarks.landmark[8])

            wrist_pos_px = wrist_pos_percent.scale(self.config.capture_size).toIntVector()
            thumb_pos_px = thumb_pos_percent.scale(self.config.capture_size).toIntVector()
            index_pos_px = index_pos_percent.scale(self.config.capture_size).toIntVector()
        except:
            return

        # draw landmark positions
        cv2.circle(frame, wrist_pos_px.toTuple2(), 5, (255, 0, 0), -1)
        cv2.circle(frame, thumb_pos_px.toTuple2(), 5, (0, 255, 255), -1)
        cv2.circle(frame, index_pos_px.toTuple2(), 5, (255, 255, 0), -1)

        # detect mouse position
        mouse_pos_px = self.get_mouse_position(wrist_pos_percent, frame)
        self.mouse_control.on_new_mouse_position_detected(mouse_pos_px)

        # detect click
        current_time_ms = get_time_ms()
        thumb_index_center_px = (thumb_pos_px + (index_pos_px - thumb_pos_px).scaleByScalar(0.5)).toIntVector()
        dist_thumb_index_percent = Vector.distance(thumb_pos_percent, index_pos_percent)
        cv2.putText(frame, f"{dist_thumb_index_percent * 100:.0f}", thumb_index_center_px.toTuple2(), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (127, 0, 127), 2)
        if (dist_thumb_index_percent < self.config.click_distance_threshold_percent):
            if (self.last_click_time_ms + self.config.click_delay_ms < current_time_ms):
                self.mouse_control.on_click_detected()
            self.last_click_time_ms = current_time_ms

    def get_mouse_position(self, screen_pos_percent: Vector, frame: Any) -> Vector:
        pos_percent_x = (screen_pos_percent.x - self.config.motion_border_left) / (1 - self.config.motion_border_left - self.config.motion_border_right)
        pos_percent_x = max(0, min(1, pos_percent_x))
        pos_percent_y = (screen_pos_percent.y - self.config.motion_border_top) / (1 - self.config.motion_border_top - self.config.motion_border_bottom)
        pos_percent_y = max(0, min(1, pos_percent_y))
        mouse_x = int(self.config.screen_offset.x + self.config.screen_size.x * pos_percent_x)
        mouse_y = int(self.config.screen_offset.y + self.config.screen_size.y * pos_percent_y)

        screen_pos_px = screen_pos_percent.scale(self.config.screen_size).toIntVector()
        cv2.putText(frame, f"{pos_percent_x * 100:.0f} | {pos_percent_y * 100:.0f}", screen_pos_px.toTuple2(), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
        
        return Vector(mouse_x, mouse_y, 0)

    def percent_to_pixels(self, pos_percent: Vector, screen_size: Vector) -> Vector:
        return Vector(pos_percent.x * screen_size.x, pos_percent.y * screen_size.y, 0)