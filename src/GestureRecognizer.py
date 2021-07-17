from __future__ import annotations
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
        self.last_left_click_time_ms = 0
        self.last_right_click_time_ms = 0
        self.distance_thumb_index_was_above_high_click_threshold_since_last_click = False
        self.distance_thumb_middle_was_above_high_click_threshold_since_last_click = False

    def process_hand_landmarks(self, frame: Any, multi_hand_landmarks: Any) -> None:
        if (len(multi_hand_landmarks) <= 0):
            return

        # find landmark positions
        try:
            first_hand_landmarks = multi_hand_landmarks[0]
            wrist_pos = FingerPosition(first_hand_landmarks.landmark[0], self.config.capture_size)
            thumb_pos = FingerPosition(first_hand_landmarks.landmark[4], self.config.capture_size)
            index_finger_pos = FingerPosition(first_hand_landmarks.landmark[8], self.config.capture_size)
            middle_finger_pos = FingerPosition(first_hand_landmarks.landmark[12], self.config.capture_size)
        except:
            return

        # draw landmark positions
        cv2.circle(frame, wrist_pos.px.toTuple2(), 5, (255, 0, 0), -1)
        cv2.circle(frame, thumb_pos.px.toTuple2(), 5, (0, 255, 255), -1)
        cv2.circle(frame, index_finger_pos.px.toTuple2(), 5, (255, 255, 0), -1)
        cv2.circle(frame, middle_finger_pos.px.toTuple2(), 5, (0, 255, 0), -1)

        # draw click threshold
        cv2.circle(frame, thumb_pos.px.toTuple2(), int(self.config.click_distance_threshold_low_percent * self.config.capture_size.x / 2), (0, 255, 0), 2)
        cv2.circle(frame, thumb_pos.px.toTuple2(), int(self.config.click_distance_threshold_high_percent * self.config.capture_size.x / 2), (0, 255, 0), 2)

        # detect mouse position
        mouse_pos_px = self.get_mouse_position_px(wrist_pos.percent, frame)
        self.mouse_control.on_new_mouse_position_detected(mouse_pos_px)

        # detect click
        current_time_ms = get_time_ms()
        self.detect_left_click(current_time_ms, thumb_pos, index_finger_pos, middle_finger_pos)
        self.detect_right_click(current_time_ms, thumb_pos, index_finger_pos, middle_finger_pos)

    def get_mouse_position_px(self, screen_pos_percent: Vector, frame: Any) -> Vector:
        pos_percent_x = (screen_pos_percent.x - self.config.motion_border_left) / (1 - self.config.motion_border_left - self.config.motion_border_right)
        pos_percent_x = max(0, min(1, pos_percent_x))
        pos_percent_y = (screen_pos_percent.y - self.config.motion_border_top) / (1 - self.config.motion_border_top - self.config.motion_border_bottom)
        pos_percent_y = max(0, min(1, pos_percent_y))
        mouse_x = int(self.config.screen_offset.x + self.config.screen_size.x * pos_percent_x)
        mouse_y = int(self.config.screen_offset.y + self.config.screen_size.y * pos_percent_y)

        screen_pos_px = screen_pos_percent.scale(self.config.screen_size).toIntVector()
        cv2.putText(frame, f"{pos_percent_x * 100:.0f} | {pos_percent_y * 100:.0f}", screen_pos_px.toTuple2(), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
        
        return Vector(mouse_x, mouse_y, 0)

    def detect_left_click(self,
            current_time_ms: int,
            thumb_pos: FingerPosition,
            index_finger_pos: FingerPosition,
            middle_finger_pos: FingerPosition) -> None:
        # left-click: (index finger near thumb) and (middle finger not near thumb).        
        distance_thumb_index_percent = Vector.distance(thumb_pos.percent, index_finger_pos.percent)
        distance_thumb_middle_percent = Vector.distance(thumb_pos.percent, middle_finger_pos.percent)
        
        if (distance_thumb_index_percent > self.config.click_distance_threshold_high_percent):
            self.distance_thumb_index_was_above_high_click_threshold_since_last_click = True

        if (not self.distance_thumb_index_was_above_high_click_threshold_since_last_click):
            return

        if (distance_thumb_index_percent < self.config.click_distance_threshold_low_percent
            and distance_thumb_middle_percent > self.config.click_distance_threshold_high_percent):
            if (self.last_left_click_time_ms + self.config.click_delay_ms < current_time_ms):
                self.on_left_click()
            self.last_left_click_time_ms = current_time_ms

    def detect_right_click(self,
            current_time_ms: int,
            thumb_pos: FingerPosition,
            index_finger_pos: FingerPosition,
            middle_finger_pos: FingerPosition) -> None:
        # right-click: (middle finger near thumb) and (index finger not near thumb).        
        distance_thumb_index_percent = Vector.distance(thumb_pos.percent, index_finger_pos.percent)
        distance_thumb_middle_percent = Vector.distance(thumb_pos.percent, middle_finger_pos.percent)
        
        if (distance_thumb_middle_percent > self.config.click_distance_threshold_high_percent):
            self.distance_thumb_middle_was_above_high_click_threshold_since_last_click = True

        if (not self.distance_thumb_middle_was_above_high_click_threshold_since_last_click):
            return

        if (distance_thumb_middle_percent < self.config.click_distance_threshold_low_percent
            and distance_thumb_index_percent > self.config.click_distance_threshold_high_percent):
            if (self.last_right_click_time_ms + self.config.click_delay_ms < current_time_ms):
                self.on_right_click()
            self.last_right_click_time_ms = current_time_ms

    def on_left_click(self) -> None:
        self.distance_thumb_index_was_above_high_click_threshold_since_last_click = False
        self.mouse_control.on_left_click_detected()

    def on_right_click(self) -> None:
        self.distance_thumb_middle_was_above_high_click_threshold_since_last_click = False
        self.mouse_control.on_right_click_detected()

class FingerPosition:
    def __init__(self, landmark: Any, capture_size: Vector) -> None:
        self.percent = Vector.from_xy(landmark)
        self.px = self.percent.scale(capture_size).toIntVector()