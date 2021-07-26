from __future__ import annotations
from typing import Any, List, cast
from cv2 import cv2 # type: ignore
from util import all_decreasing, all_increasing, get_min_element, get_time_ms, get_elements_except
from MouseControl import MouseControl
from Config import Config
from Vector import Vector
from itertools import chain

class GestureRecognizer:
    wrist_index = 0
    thumb_finger_indexes = [1, 2, 3, 4]
    index_finger_indexes = [5, 6, 7, 8]
    middle_finger_indexes = [9, 10, 11, 12]
    ring_finger_indexes = [13, 14, 15, 16]
    pinky_finger_indexes = [17, 18, 19, 20]

    def __init__(self, config: Config, mouse_control: MouseControl):
        self.config = config
        self.mouse_control = mouse_control
        self.last_left_click_time_ms = 0
        self.last_right_click_time_ms = 0
        self.distance_thumb_index_was_above_high_click_threshold_since_last_click = False
        self.distance_thumb_middle_was_above_high_click_threshold_since_last_click = False
        
        self.left_click_count = 0
        self.left_click_start_time_ms = 0

        self.is_potential_drag_gesture = False
        self.is_drag_started = False

        self.last_scroll_time_ms = 0
        self.start_scroll_time_ms = 0
        self.was_thumbs_up_last_frame = False

    def process_hand_landmarks(self, frame: Any, multi_hand_landmarks: Any) -> None:
        if (len(multi_hand_landmarks) <= 0):
            return

        # find landmark positions
        try:
            first_hand_landmarks = multi_hand_landmarks[0]
            wrist_pos = FingerPosition(first_hand_landmarks.landmark[GestureRecognizer.wrist_index], self.config.capture_size)
            thumb_pos = FingerPosition(first_hand_landmarks.landmark[GestureRecognizer.thumb_finger_indexes[-1]], self.config.capture_size)
            index_finger_pos = FingerPosition(first_hand_landmarks.landmark[GestureRecognizer.index_finger_indexes[-1]], self.config.capture_size)
            middle_finger_pos = FingerPosition(first_hand_landmarks.landmark[GestureRecognizer.middle_finger_indexes[-1]], self.config.capture_size)
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

        # detect drag
        self.detect_drag(current_time_ms, thumb_pos, index_finger_pos)

        # detect scroll
        self.detect_scoll(current_time_ms, first_hand_landmarks)

    def get_mouse_position_px(self, screen_pos_percent: Vector, frame: Any) -> Vector:
        pos_percent_x = (screen_pos_percent.x - self.config.motion_border_left) / (1 - self.config.motion_border_left - self.config.motion_border_right)
        pos_percent_x = max(0, min(1, pos_percent_x))
        pos_percent_y = (screen_pos_percent.y - self.config.motion_border_top) / (1 - self.config.motion_border_top - self.config.motion_border_bottom)
        pos_percent_y = max(0, min(1, pos_percent_y))
        mouse_x = int(self.config.screen_offset.x + self.config.screen_size.x * pos_percent_x)
        mouse_y = int(self.config.screen_offset.y + self.config.screen_size.y * pos_percent_y)

        screen_pos_px = screen_pos_percent.scale(self.config.capture_size).add(Vector(10, 10)).toIntVector()
        pos_text = f"{pos_percent_x * 100:.0f} ({mouse_x}) | {pos_percent_y * 100:.0f} ({mouse_y})"
        cv2.putText(frame, pos_text, screen_pos_px.toTuple2(), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
        
        return Vector(mouse_x, mouse_y, 0)

    def detect_scoll(self,
            current_time_ms: int,
            first_hand_landmarks: Any) -> None:
        # scroll up gesture: thumbs up
        # scroll down gesture: thumbs up, i.e., thumb is stretched and downwards, other fingers curved and vertically aligned
        finger_positions = HandFingerPositions(first_hand_landmarks, self.config.capture_size)

        is_thumbs_up = self.is_thumbs_up(finger_positions)
        if (not is_thumbs_up):
            self.start_scroll_time_ms = 0
            
        if (is_thumbs_up and not self.was_thumbs_up_last_frame):
            self.start_scroll_time_ms = current_time_ms

        scroll_pause_ms = self.config.initial_scroll_pause_ms
        if self.start_scroll_time_ms + self.config.initial_scroll_pause_ms < current_time_ms:
            scroll_pause_ms = self.config.continued_scroll_pause_ms

        if (is_thumbs_up
                and (self.last_scroll_time_ms == 0
                     or self.last_scroll_time_ms + scroll_pause_ms < current_time_ms)):
            self.on_scroll_up(current_time_ms)

        self.was_thumbs_up_last_frame = is_thumbs_up

    def detect_drag(self,
            current_time_ms: int,
            thumb_pos: FingerPosition,
            index_finger_pos: FingerPosition) -> None:
        # drag start gesture: holding a click gesture (index near thumb for a longer time)
        # drag end gesture: releasing click gesture (index not near thumb anymore)
        distance_thumb_index_percent = Vector.distance(thumb_pos.percent, index_finger_pos.percent)

        if (distance_thumb_index_percent > self.config.click_distance_threshold_high_percent):
            self.is_potential_drag_gesture = False

        if (self.is_drag_started
                and not self.is_potential_drag_gesture):
            self.on_end_drag()
            return

        if (not self.is_drag_started
                and self.is_potential_drag_gesture
                and self.left_click_start_time_ms + self.config.drag_start_click_delay_ms < current_time_ms):
            self.on_begin_drag()

    def detect_left_click(self,
            current_time_ms: int,
            thumb_pos: FingerPosition,
            index_finger_pos: FingerPosition,
            middle_finger_pos: FingerPosition) -> None:
        # left-click gesture: (index finger near thumb) and (middle finger not near thumb).        
        distance_thumb_index_percent = Vector.distance(thumb_pos.percent, index_finger_pos.percent)
        distance_thumb_middle_percent = Vector.distance(thumb_pos.percent, middle_finger_pos.percent)
        
        if (self.last_left_click_time_ms + self.config.single_click_pause_ms <= current_time_ms):
            self.left_click_count = 0

        if (distance_thumb_index_percent > self.config.click_distance_threshold_high_percent):
            self.distance_thumb_index_was_above_high_click_threshold_since_last_click = True

        if (not self.distance_thumb_index_was_above_high_click_threshold_since_last_click):
            return

        if (distance_thumb_index_percent < self.config.click_distance_threshold_low_percent
            and distance_thumb_middle_percent > self.config.click_distance_threshold_high_percent):
            
            if (self.left_click_count == 0
                    and self.last_left_click_time_ms + self.config.single_click_pause_ms < current_time_ms):
                self.on_left_click(current_time_ms)
            elif (self.left_click_count == 1
                    and current_time_ms < self.last_left_click_time_ms + self.config.double_click_max_pause_ms):
                self.on_double_left_click()
            self.last_left_click_time_ms = current_time_ms

    def detect_right_click(self,
            current_time_ms: int,
            thumb_pos: FingerPosition,
            index_finger_pos: FingerPosition,
            middle_finger_pos: FingerPosition) -> None:
        # right-click gesture: (middle finger near thumb) and (index finger not near thumb).        
        distance_thumb_index_percent = Vector.distance(thumb_pos.percent, index_finger_pos.percent)
        distance_thumb_middle_percent = Vector.distance(thumb_pos.percent, middle_finger_pos.percent)
        
        if (distance_thumb_middle_percent > self.config.click_distance_threshold_high_percent):
            self.distance_thumb_middle_was_above_high_click_threshold_since_last_click = True

        if (not self.distance_thumb_middle_was_above_high_click_threshold_since_last_click):
            return

        if (distance_thumb_middle_percent < self.config.click_distance_threshold_low_percent
            and distance_thumb_index_percent > self.config.click_distance_threshold_high_percent):
            
            if (self.last_right_click_time_ms + self.config.single_click_pause_ms < current_time_ms):
                self.on_right_click()
            self.last_right_click_time_ms = current_time_ms

    def is_thumbs_up(self,
            hand_finger_positions: HandFingerPositions) -> bool:
        # thumbs up: thumb is stretched and upwards, other fingers curved and vertically aligned
        
        # thumb must be vertically aligned upwards
        if (not self.is_vertically_aligned_upwards(hand_finger_positions.thumb_finger_positions)):
            return False

        # thumb must be at the top
        relevant_thumb_positions = get_elements_except(hand_finger_positions.thumb_finger_positions, [hand_finger_positions.thumb_finger_positions[0]])
        lowest_thumb_joint = get_min_element(relevant_thumb_positions, lambda finger_position: finger_position.px.y)
        all_finger_positions_except_thumb = get_elements_except(hand_finger_positions.all_finger_positions, hand_finger_positions.thumb_finger_positions)
        is_thumb_at_top = all(finger_position.px.y > lowest_thumb_joint.px.y for finger_position in all_finger_positions_except_thumb)
        if (not is_thumb_at_top):
            return False

        # other finger joints are vertically aligned
        first_column_finger_positions = hand_finger_positions.get_finger_positions_by_index([5, 9, 13, 17])
        second_column_finger_positions = hand_finger_positions.get_finger_positions_by_index([6, 10, 14, 18])
        third_column_finger_positions = hand_finger_positions.get_finger_positions_by_index([7, 11, 15, 19])
        fourth_column_finger_positions = hand_finger_positions.get_finger_positions_by_index([8, 12, 16, 20])
        all_columns_vertically_aligned = all(self.is_vertically_aligned_downwards(column_finger_positions)
                for column_finger_positions in [first_column_finger_positions,
                                                second_column_finger_positions,
                                                third_column_finger_positions,
                                                fourth_column_finger_positions])
        if (not all_columns_vertically_aligned):
            return False

        # other fingers are curved
        if (self.is_finger_straight_horizontally(hand_finger_positions.index_finger_positions)
                or self.is_finger_straight_horizontally(hand_finger_positions.middle_finger_positions)
                or self.is_finger_straight_horizontally(hand_finger_positions.ring_finger_positions)
                or self.is_finger_straight_horizontally(hand_finger_positions.pinky_finger_positions)):
            return False

        return True

    def is_finger_straight_horizontally(self, finger_positions: List[FingerPosition]) -> bool:
        # strechted finger joints: 0-1-2
        # curved finger joints: 0-2-1
        if (all_increasing(finger_positions, lambda finger_position: finger_position.px.x)
                or all_decreasing(finger_positions, lambda finger_position: finger_position.px.x)):
            return True

        return False

    def is_vertically_aligned_upwards(self,
            finger_positions: List[FingerPosition]) -> bool:

        for i in range(1, len(finger_positions)):
            if (finger_positions[i - 1].px.y < finger_positions[i].px.y):
                return False
        return True

    def is_vertically_aligned_downwards(self,
            finger_positions: List[FingerPosition]) -> bool:

        for i in range(1, len(finger_positions)):
            if (finger_positions[i - 1].px.y > finger_positions[i].px.y):
                return False
        return True

    def on_left_click(self, current_time_ms: int) -> None:
        self.distance_thumb_index_was_above_high_click_threshold_since_last_click = False
        self.left_click_count = self.left_click_count + 1
        self.mouse_control.on_left_click_detected()
        self.is_potential_drag_gesture = True
        self.left_click_start_time_ms = current_time_ms

    def on_double_left_click(self) -> None:
        self.distance_thumb_index_was_above_high_click_threshold_since_last_click = False
        self.left_click_count = 2
        self.mouse_control.on_double_left_click_detected()

    def on_right_click(self) -> None:
        self.distance_thumb_middle_was_above_high_click_threshold_since_last_click = False
        self.mouse_control.on_right_click_detected()

    def on_begin_drag(self) -> None:
        self.is_drag_started = True
        self.mouse_control.on_begin_drag()

    def on_end_drag(self) -> None:
        self.is_drag_started = False
        self.is_potential_drag_gesture = False
        self.mouse_control.on_end_drag()

    def on_scroll_up(self, current_time_ms: int) -> None:
        self.last_scroll_time_ms = current_time_ms
        self.mouse_control.on_scroll_up()

class HandFingerPositions:
    def __init__(self, single_hand_landmarks: Any, capture_size: Vector) -> None:
        self.single_hand_landmarks = single_hand_landmarks
        
        self.wrist_position = FingerPosition(single_hand_landmarks.landmark[GestureRecognizer.wrist_index], capture_size)
        self.thumb_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.thumb_finger_indexes, capture_size)
        self.index_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.index_finger_indexes, capture_size)
        self.middle_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.middle_finger_indexes, capture_size)
        self.ring_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.ring_finger_indexes, capture_size)
        self.pinky_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.pinky_finger_indexes, capture_size)
        
        self.all_finger_positions = list(chain.from_iterable([self.thumb_finger_positions,
            self.index_finger_positions,
            self.middle_finger_positions,
            self.ring_finger_positions,
            self.pinky_finger_positions]))

        self.index_to_finger_position = {0: self.wrist_position,
            1: self.thumb_finger_positions[0],
            2: self.thumb_finger_positions[1],
            3: self.thumb_finger_positions[2],
            4: self.thumb_finger_positions[3],

            5: self.index_finger_positions[0],
            6: self.index_finger_positions[1],
            7: self.index_finger_positions[2],
            8: self.index_finger_positions[3],
            
            9: self.middle_finger_positions[0],
            10: self.middle_finger_positions[1],
            11: self.middle_finger_positions[2],
            12: self.middle_finger_positions[3],
            
            13: self.ring_finger_positions[0],
            14: self.ring_finger_positions[1],
            15: self.ring_finger_positions[2],
            16: self.ring_finger_positions[3],
            
            17: self.pinky_finger_positions[0],
            18: self.pinky_finger_positions[1],
            19: self.pinky_finger_positions[2],
            20: self.pinky_finger_positions[3],
        }

    def get_finger_positions_from_hand_landmarks(self,
            finger_indexes: List[int],
            capture_size: Vector) -> List[FingerPosition]:
        return [FingerPosition(self.single_hand_landmarks.landmark[i], capture_size) for i in finger_indexes]

    def get_finger_position_by_index(self, index: int) -> FingerPosition:
        return self.index_to_finger_position[index]

    def get_finger_positions_by_index(self, indexes: List[int]) -> List[FingerPosition]:
        return [self.get_finger_position_by_index(index) for index in indexes]

class FingerPosition:
    def __init__(self, landmark: Any, capture_size: Vector) -> None:
        self.percent = Vector.from_xy(landmark)
        self.px = self.percent.scale(capture_size).toIntVector()