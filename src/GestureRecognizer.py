from __future__ import annotations
from enum import Enum
from typing import Any, List
from itertools import chain
from cv2 import cv2 # type: ignore
from LogHolder import LogHolder # type: ignore
from util import all_decreasing, all_increasing, get_min_element, get_max_element, get_time_ms, get_elements_except
from MouseControl import MouseButton, MouseControl
from Config import Config
from Vector import Vector

class GestureRecognizer(LogHolder):
    wrist_index = 0
    thumb_finger_indexes = [1, 2, 3, 4]
    index_finger_indexes = [5, 6, 7, 8]
    middle_finger_indexes = [9, 10, 11, 12]
    ring_finger_indexes = [13, 14, 15, 16]
    pinky_finger_indexes = [17, 18, 19, 20]

    def __init__(self, config: Config, mouse_control: MouseControl):
        super().__init__()
        self.config = config
        self.mouse_control = mouse_control
        self.last_left_click_time_ms = 0
        self.last_right_click_time_ms = 0
        self.last_middle_click_time_ms = 0
        self.allow_left_click = False
        self.allow_right_click = False
        self.allow_middle_click = False
        
        self.left_click_count = 0
        self.left_click_start_time_ms = 0

        self.is_potential_drag_gesture = False
        self.is_drag_started = False

        self.last_scroll_time_ms = 0
        self.start_scroll_time_ms = 0
        self.was_thumb_up_last_frame = False
        self.was_thumb_down_last_frame = False

    def process_hand_landmarks(self, frame: Any, multi_hand_landmarks: Any) -> None:
        if (len(multi_hand_landmarks) <= 0):
            return

        # find landmark positions
        first_hand_landmarks = multi_hand_landmarks[0]
        hand_finger_positions = HandFingerPositions(first_hand_landmarks, self.config.capture_size.value)

        wrist_position = hand_finger_positions.wrist_position
        thumb_tip_position = hand_finger_positions.thumb_finger_positions[-1]
        index_finger_position = hand_finger_positions.index_finger_positions[-1]
        middle_finger_position = hand_finger_positions.middle_finger_positions[-1]

        # draw landmark positions
        cv2.circle(frame, wrist_position.px.to_tuple_2(), 5, (255, 0, 0), -1)
        cv2.circle(frame, thumb_tip_position.px.to_tuple_2(), 5, (0, 255, 255), -1)
        cv2.circle(frame, index_finger_position.px.to_tuple_2(), 5, (255, 255, 0), -1)
        cv2.circle(frame, middle_finger_position.px.to_tuple_2(), 5, (0, 255, 0), -1)

        # draw click threshold
        cv2.circle(frame, thumb_tip_position.px.to_tuple_2(), int(self.config.click_distance_threshold_low_percent.value * self.config.capture_size.value.x / 2), (0, 255, 0), 2)
        cv2.circle(frame, thumb_tip_position.px.to_tuple_2(), int(self.config.click_distance_threshold_high_percent.value * self.config.capture_size.value.x / 2), (0, 255, 0), 2)

        # detect mouse position
        mouse_pos_px = self.get_mouse_position_px(wrist_position.percent, frame)
        self.mouse_control.on_new_mouse_position_detected(mouse_pos_px)

        # detect click
        current_time_ms = get_time_ms()
        self.detect_left_click(current_time_ms, hand_finger_positions)
        self.detect_right_click(current_time_ms, hand_finger_positions)
        self.detect_middle_click(current_time_ms, hand_finger_positions)

        # detect drag
        self.detect_drag(current_time_ms, thumb_tip_position, index_finger_position)

        # detect scroll
        self.detect_scoll(current_time_ms, hand_finger_positions)

    def get_mouse_position_px(self, screen_pos_percent: Vector, frame: Any) -> Vector:
        pos_percent_x = (screen_pos_percent.x - self.config.motion_border_left.value) / (1 - self.config.motion_border_left.value - self.config.motion_border_right.value)
        pos_percent_x = max(0, min(1, pos_percent_x))
        pos_percent_y = (screen_pos_percent.y - self.config.motion_border_top.value) / (1 - self.config.motion_border_top.value - self.config.motion_border_bottom.value)
        pos_percent_y = max(0, min(1, pos_percent_y))
        mouse_x = int(self.config.screen_offset.value.x + self.config.screen_size.value.x * pos_percent_x)
        mouse_y = int(self.config.screen_offset.value.y + self.config.screen_size.value.y * pos_percent_y)

        screen_pos_px = screen_pos_percent.scale(self.config.capture_size.value).add(Vector(10, 10)).to_int_vector()
        pos_text = f"{pos_percent_x * 100:.0f}% ({mouse_x}px) | {pos_percent_y * 100:.0f}% ({mouse_y}px)"
        cv2.putText(frame, pos_text, screen_pos_px.to_tuple_2(), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
        
        return Vector(mouse_x, mouse_y, 0)

    def detect_scoll(self,
            current_time_ms: int,
            hand_finger_positions: HandFingerPositions) -> None:
        # scroll up gesture: thumb up
        # scroll down gesture: thumb down

        # scrolling down is more common, thus check first thumb-down gesture
        is_thumb_down = self.is_thumb_down(hand_finger_positions)
        # thumb-up gesture is a relatively complex calculation, thus assume false if thumb-down gesture has been detected already.
        is_thumb_up = not is_thumb_down and self.is_thumb_up(hand_finger_positions)

        if (not is_thumb_up and not is_thumb_down):
            # not scrolling in any direction
            self.start_scroll_time_ms = 0
        
        # find risink flank of thumb gesture
        is_initial_scroll = False
        if ((is_thumb_up and not self.was_thumb_up_last_frame)
                or (is_thumb_down and not self.was_thumb_down_last_frame)):
            self.start_scroll_time_ms = current_time_ms
            is_initial_scroll = True

        if is_thumb_up or is_thumb_down:
            is_continued_scroll_mode = self.start_scroll_time_ms + self.config.continued_scroll_mode_delay_ms.value <= current_time_ms
            is_continued_scroll_needed = self.last_scroll_time_ms + self.config.continued_scroll_pause_ms.value <= current_time_ms
            is_scroll_needed_now = is_initial_scroll or (is_continued_scroll_mode and is_continued_scroll_needed)
            if (is_scroll_needed_now):
                if (is_thumb_up):
                    self.on_scroll(0, 1, current_time_ms)
                if (is_thumb_down):
                    self.on_scroll(0, -1, current_time_ms)

        self.was_thumb_up_last_frame = is_thumb_up
        self.was_thumb_down_last_frame = is_thumb_down

    def detect_drag(self,
            current_time_ms: int,
            thumb_pos: FingerPosition,
            index_finger_pos: FingerPosition) -> None:
        # drag start gesture: holding a click gesture (index near thumb for a longer time)
        # drag end gesture: releasing click gesture (index not near thumb anymore)
        distance_thumb_index_percent = Vector.distance(thumb_pos.percent, index_finger_pos.percent)

        if (distance_thumb_index_percent > self.config.click_distance_threshold_high_percent.value):
            self.is_potential_drag_gesture = False

        if (self.is_drag_started
                and not self.is_potential_drag_gesture):
            self.on_end_drag()
            return

        if (not self.is_drag_started
                and self.is_potential_drag_gesture
                and self.left_click_start_time_ms + self.config.drag_start_click_delay_ms.value <= current_time_ms):
            self.on_begin_drag()

    def detect_left_click(self,
            current_time_ms: int,
            hand_finger_positions: HandFingerPositions) -> None:
        # left-click gesture: (index finger near thumb) and (other fingers not near thumb).        

        index_finger_tip = hand_finger_positions.index_finger_positions[-1]
        thumb_finger_tip = hand_finger_positions.thumb_finger_positions[-1]
        if (self.is_faraway_target([index_finger_tip], thumb_finger_tip)):
            self.allow_left_click = True

        if (not self.allow_left_click):
            return

        if (self.last_left_click_time_ms + self.config.single_click_pause_ms.value <= current_time_ms):
            self.left_click_count = 0

        middle_finger_tip = hand_finger_positions.middle_finger_positions[-1]
        ring_finger_tip = hand_finger_positions.ring_finger_positions[-1]
        pinky_finger_tip = hand_finger_positions.pinky_finger_positions[-1]
        if (self.is_near_target([index_finger_tip], thumb_finger_tip)
                and self.is_faraway_target([middle_finger_tip, ring_finger_tip, pinky_finger_tip], thumb_finger_tip)):
            if (self.left_click_count == 0
                    and self.last_left_click_time_ms + self.config.single_click_pause_ms.value <= current_time_ms):
                self.on_left_click(current_time_ms)
            elif (self.left_click_count == 1
                    and current_time_ms < self.last_left_click_time_ms + self.config.double_click_max_pause_ms.value):
                self.on_double_left_click(current_time_ms)
    
    def is_faraway_target(self,
            finger_positions: List[FingerPosition],
            target_position: FingerPosition) -> bool:
        finger_target_distances_percent = [Vector.distance(finger_position.percent, target_position.percent) for finger_position in finger_positions]

        all_fingers_not_near_target = all(distance_percent > self.config.click_distance_threshold_high_percent.value
            for distance_percent in finger_target_distances_percent)

        return all_fingers_not_near_target

    def is_near_target(self,
            finger_positions: List[FingerPosition],
            target_position: FingerPosition) -> bool:
        finger_target_distances_percent = [Vector.distance(finger_position.percent, target_position.percent) for finger_position in finger_positions]

        all_fingers_near_target = all(distance_percent < self.config.click_distance_threshold_low_percent.value
            for distance_percent in finger_target_distances_percent)

        return all_fingers_near_target

    def detect_right_click(self,
            current_time_ms: int,
            hand_finger_positions: HandFingerPositions) -> None:
        # right-click gesture: (middle and ring fingers near thumb) and (other fingers not near thumb).        
        
        middle_finger_tip = hand_finger_positions.middle_finger_positions[-1]
        ring_finger_tip = hand_finger_positions.ring_finger_positions[-1]
        thumb_finger_tip = hand_finger_positions.thumb_finger_positions[-1]
        if (self.is_faraway_target([middle_finger_tip, ring_finger_tip], thumb_finger_tip)):
            self.allow_right_click = True

        if (not self.allow_right_click):
            return

        index_finger_tip = hand_finger_positions.index_finger_positions[-1]
        pinky_finger_tip = hand_finger_positions.pinky_finger_positions[-1]
        if (self.is_near_target([middle_finger_tip, ring_finger_tip], thumb_finger_tip)
                and self.is_faraway_target([index_finger_tip, pinky_finger_tip], thumb_finger_tip)):
            if (self.last_right_click_time_ms + self.config.single_click_pause_ms.value <= current_time_ms):
                self.on_right_click(current_time_ms)

    def detect_middle_click(self,
            current_time_ms: int,
            hand_finger_positions: HandFingerPositions) -> None:
        # middle-click gesture: (ring and pinky fingers near thumb) and (other fingers not near thumb).        
        
        ring_finger_tip = hand_finger_positions.ring_finger_positions[-1]
        pinky_finger_tip = hand_finger_positions.pinky_finger_positions[-1]
        thumb_finger_tip = hand_finger_positions.thumb_finger_positions[-1]
        if (self.is_faraway_target([ring_finger_tip, pinky_finger_tip], thumb_finger_tip)):
            self.allow_middle_click = True

        if (not self.allow_middle_click):
            return

        index_finger_tip = hand_finger_positions.index_finger_positions[-1]
        middle_finger_tip = hand_finger_positions.middle_finger_positions[-1]
        if (self.is_near_target([ring_finger_tip, pinky_finger_tip], thumb_finger_tip)
                and self.is_faraway_target([index_finger_tip, middle_finger_tip], thumb_finger_tip)):
            if (self.last_middle_click_time_ms + self.config.single_click_pause_ms.value <= current_time_ms):
                self.on_middle_click(current_time_ms)

    def is_thumb_up(self,
            hand_finger_positions: HandFingerPositions) -> bool:
        # thumbs up: thumb is stretched and upwards, other fingers curved and vertically aligned
        
        # thumb must be vertically aligned upwards
        if (not self.is_vertically_aligned_upwards(hand_finger_positions.thumb_finger_positions)):
            return False
        
        # thumb must be at the top
        relevant_thumb_positions = get_elements_except(hand_finger_positions.thumb_finger_positions, [hand_finger_positions.thumb_finger_positions[0], hand_finger_positions.thumb_finger_positions[1]])
        lowest_thumb_joint = get_min_element(relevant_thumb_positions, lambda finger_position: finger_position.px.y)
        all_finger_positions_except_thumb = get_elements_except(hand_finger_positions.all_finger_positions, hand_finger_positions.thumb_finger_positions)
        is_thumb_at_top = all(finger_position.px.y > lowest_thumb_joint.px.y for finger_position in all_finger_positions_except_thumb)
        if (not is_thumb_at_top):
            return False

        # other finger joints are vertically aligned and curved
        if (not self.is_fingers_aligned_for_thumb_up_or_thumb_down(hand_finger_positions, ThumbGestureDirection.UP)):
            return False

        return True

    def is_thumb_down(self,
            hand_finger_positions: HandFingerPositions) -> bool:
        # thumbs down: thumb is stretched and downwards, other fingers curved and vertically aligned
        
        # thumb must be vertically aligned downwards
        if (not self.is_vertically_aligned_downwards(hand_finger_positions.thumb_finger_positions)):
            return False

        # thumb must be at the bottom
        relevant_thumb_positions = get_elements_except(hand_finger_positions.thumb_finger_positions, [hand_finger_positions.thumb_finger_positions[0], hand_finger_positions.thumb_finger_positions[1]])
        highest_thumb_joint = get_max_element(relevant_thumb_positions, lambda finger_position: finger_position.px.y)
        all_finger_positions_except_thumb = get_elements_except(hand_finger_positions.all_finger_positions, hand_finger_positions.thumb_finger_positions)
        is_thumb_at_bottom = all(finger_position.px.y < highest_thumb_joint.px.y for finger_position in all_finger_positions_except_thumb)
        if (not is_thumb_at_bottom):
            return False
        
        # other finger joints are vertically aligned and curved
        if (not self.is_fingers_aligned_for_thumb_up_or_thumb_down(hand_finger_positions, ThumbGestureDirection.DOWN)):
            return False
        
        return True

    def is_fingers_aligned_for_thumb_up_or_thumb_down(self, hand_finger_positions: HandFingerPositions, direction: ThumbGestureDirection) -> bool:
        # Fingers are curved
        if (self.is_finger_straight_horizontally(hand_finger_positions.index_finger_positions)
                or self.is_finger_straight_horizontally(hand_finger_positions.middle_finger_positions)
                or self.is_finger_straight_horizontally(hand_finger_positions.ring_finger_positions)
                or self.is_finger_straight_horizontally(hand_finger_positions.pinky_finger_positions)):
            return False

        # Finger joints are vertically aligned.
        # Note that depending on the gesture, the camera is faced with different joints
        if direction == ThumbGestureDirection.UP:
            vertically_aligned_check_function = self.is_vertically_aligned_downwards
            relevant_column_finger_positions = hand_finger_positions.get_finger_positions_by_index([5, 9, 13, 17])
        elif direction == ThumbGestureDirection.DOWN:
            vertically_aligned_check_function = self.is_vertically_aligned_upwards
            relevant_column_finger_positions = hand_finger_positions.get_finger_positions_by_index([6, 10, 14, 18])
        else:
            raise Exception(f"Unsupported ThumbGestureDirection {direction}")

        all_columns_vertically_aligned = all(vertically_aligned_check_function(column_finger_positions)
                for column_finger_positions in [relevant_column_finger_positions])
        return all_columns_vertically_aligned

    def is_finger_straight_horizontally(self, finger_positions: List[FingerPosition]) -> bool:
        # stretched finger joints: 0-1-2
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
        self.allow_left_click = False
        self.left_click_count = self.left_click_count + 1
        self.mouse_control.on_single_click_detected(MouseButton.LEFT)
        self.is_potential_drag_gesture = True
        self.left_click_start_time_ms = current_time_ms
        self.last_left_click_time_ms = current_time_ms

    def on_double_left_click(self, current_time_ms: int) -> None:
        self.allow_left_click = False
        self.left_click_count = 2
        self.mouse_control.on_double_left_click_detected()
        self.last_left_click_time_ms = current_time_ms

    def on_right_click(self, current_time_ms: int) -> None:
        self.allow_right_click = False
        self.mouse_control.on_single_click_detected(MouseButton.RIGHT)
        self.last_right_click_time_ms = current_time_ms

    def on_middle_click(self, current_time_ms: int) -> None:
        self.allow_middle_click = False
        self.mouse_control.on_single_click_detected(MouseButton.MIDDLE)
        self.last_middle_click_time_ms = current_time_ms

    def on_begin_drag(self) -> None:
        self.is_drag_started = True
        self.mouse_control.on_begin_drag()

    def on_end_drag(self) -> None:
        self.is_drag_started = False
        self.is_potential_drag_gesture = False
        self.mouse_control.on_end_drag()

    def on_scroll(self, x: int, y: int, current_time_ms: int) -> None:
        self.last_scroll_time_ms = current_time_ms
        self.mouse_control.on_scroll(x, y)

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

        self.index_to_finger_position = {
            0: self.wrist_position,
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
        self.px = self.percent.scale(capture_size).to_int_vector()

class ThumbGestureDirection(Enum):
    UP = 1
    DOWN = 2