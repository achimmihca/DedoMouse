from __future__ import annotations
from enum import Enum
from typing import Any, List, Union
import mediapipe # type: ignore
import common.AppContext as AppContext
from .LogHolder import LogHolder
from .Config import MousePositioningMode
from .Config import DisableMousePositioningTrigger
from .util import all_decreasing, all_increasing, get_min_element, get_max_element, get_time_ms, get_elements_except, limit_float
from .draw_util import put_text
from .MouseControl import MouseButton
from .ReactiveProperty import ReactiveProperty
from .Vector import Vector
from .HandFingerPositions import HandFingerPositions
from .FingerPosition import FingerPosition
from .SignalFlankRecognizer import SignalFlankRecognizer
from .SignalHoldRecognizer import SignalHoldRecognizer

class GestureRecognizer(LogHolder):
    wrist_index = 0
    thumb_finger_indexes = [1, 2, 3, 4]
    index_finger_indexes = [5, 6, 7, 8]
    middle_finger_indexes = [9, 10, 11, 12]
    ring_finger_indexes = [13, 14, 15, 16]
    pinky_finger_indexes = [17, 18, 19, 20]

    def __init__(self, app_context: AppContext.AppContext):
        super().__init__()
        self.app_context = app_context
        self.config = app_context.config
        self.mouse_control = app_context.mouse_control

        self.mediapipe_hands = mediapipe.solutions.hands.Hands(max_num_hands=1)

        self.is_potential_left_click_gesture = False
        self.last_index_near_thumb_gesture_time_ms = 0
        self.last_left_click_time_ms = 0
        self.last_right_click_time_ms = 0
        self.last_middle_click_time_ms = 0
        self.potential_left_click_start_time_ms = 0
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

        # The time is increased if in a frame there were no mouse or remarkable jitter in the finger tracking.
        # Then this duration is waited until finger tracking is stable again.
        self.jitter_pause_time_ms = ReactiveProperty(0.0)
        self.last_frame_analysis_time_ms = get_time_ms()

        # gesture flank recognizers
        self.index_near_thumb_flank_recognizer = SignalFlankRecognizer(False)
        self.middle_and_ring_near_thumb_flank_recognizer = SignalFlankRecognizer(False)
        self.ring_and_pinky_near_thumb_flank_recognizer = SignalFlankRecognizer(False)

        # left click gesture
        self.left_click_gesture_recognizer = SignalHoldRecognizer(self.index_near_thumb_flank_recognizer, lambda: self.config.click_delay_ms.value)
        self.left_click_gesture_recognizer.hold_high_event_stream.subscribe(self.on_left_click_gesture_change)

        # double click gesture
        self.index_near_thumb_flank_recognizer.rising_flank_event_stream.subscribe(self.on_index_near_thumb_rising_flank)

        # drag gesture
        self.drag_gesture_recognizer = SignalHoldRecognizer(self.index_near_thumb_flank_recognizer, lambda: self.config.click_delay_ms.value + self.config.drag_start_click_delay_ms.value)
        self.drag_gesture_recognizer.hold_high_event_stream.subscribe(self.on_drag_gesture_change)

        # right click gesture
        self.right_click_gesture_recognizer = SignalHoldRecognizer(self.middle_and_ring_near_thumb_flank_recognizer, lambda: self.config.click_delay_ms.value)
        self.right_click_gesture_recognizer.hold_high_event_stream.subscribe(self.on_right_click_gesture_change)

        # middle click gesture
        self.middle_click_gesture_recognizer = SignalHoldRecognizer(self.ring_and_pinky_near_thumb_flank_recognizer, lambda: self.config.click_delay_ms.value)
        self.middle_click_gesture_recognizer.hold_high_event_stream.subscribe(self.on_middle_click_gesture_change)

    def process_frame(self, frame: Any) -> Union[HandFingerPositions, None]:
        hand_finger_positions = None
        mediapipe_results = self.mediapipe_hands.process(frame)
        delta_time_ms = get_time_ms() - self.last_frame_analysis_time_ms
        if mediapipe_results.multi_hand_landmarks and len(mediapipe_results.multi_hand_landmarks) > 0:
            if (self.jitter_pause_time_ms.value > 0):
                # ignore finger positions until it is more stable
                self.jitter_pause_time_ms.value = self.jitter_pause_time_ms.value - delta_time_ms
            else:
                hand_finger_positions = self.process_hand_landmarks(frame, mediapipe_results.multi_hand_landmarks)
        else:
            self.jitter_pause_time_ms.value = limit_float(self.jitter_pause_time_ms.value + (delta_time_ms * 3), 0, self.config.max_jitter_pause_time_ms.value)
            if self.jitter_pause_time_ms.value > 0.4:
                self.mouse_control.last_mouse_position = None

        self.last_frame_analysis_time_ms = get_time_ms()
        return hand_finger_positions

    def process_hand_landmarks(self, frame: Any, multi_hand_landmarks: Any) -> HandFingerPositions:
        # find landmark positions
        first_hand_landmarks = multi_hand_landmarks[0]
        hand_finger_positions = HandFingerPositions(first_hand_landmarks, self.app_context.webcam_control.actual_capture_size)

        # detect mouse position
        self.detect_mouse_position(frame, hand_finger_positions)

        # detect click gestures
        current_time_ms = get_time_ms()
        is_only_index_near_thumb = self.detect_index_near_thumb_gesture(hand_finger_positions)
        self.detect_middle_and_ring_near_thumb_gesture(hand_finger_positions)
        self.detect_ring_and_pinky_near_thumb_gesture(hand_finger_positions)

        # reset click count
        if (not is_only_index_near_thumb
                and self.last_index_near_thumb_gesture_time_ms + self.config.double_click_max_pause_ms.value < current_time_ms):
            self.left_click_count = 0

        # detect scroll
        self.detect_scoll(current_time_ms, hand_finger_positions)

        # update hold gesture recognizers
        self.left_click_gesture_recognizer.update(current_time_ms)
        self.right_click_gesture_recognizer.update(current_time_ms)
        self.middle_click_gesture_recognizer.update(current_time_ms)
        self.drag_gesture_recognizer.update(current_time_ms)

        return hand_finger_positions

    def detect_mouse_position(self, frame: Any, hand_finger_positions: HandFingerPositions) -> None:
        all_fingers_near_thumb = self.is_near_target([hand_finger_positions.index_tip_position,
                                                      hand_finger_positions.middle_tip_position,
                                                      hand_finger_positions.ring_tip_position,
                                                      hand_finger_positions.pinky_tip_position],
                                                     hand_finger_positions.thumb_tip_position)
        all_fingers_faraway_thumb = self.is_faraway_target([hand_finger_positions.index_tip_position,
                                                            hand_finger_positions.middle_tip_position,
                                                            hand_finger_positions.ring_tip_position,
                                                            hand_finger_positions.pinky_tip_position],
                                                           hand_finger_positions.thumb_tip_position)
        if ((all_fingers_near_thumb and self.config.disable_mouse_positioning_trigger.value == DisableMousePositioningTrigger.ALL_FINGERS_NEAR_THUMB)
                or (not all_fingers_near_thumb and self.config.disable_mouse_positioning_trigger.value == DisableMousePositioningTrigger.ANY_FINGER_FARAWAY_THUMB)
                or (all_fingers_faraway_thumb and self.config.disable_mouse_positioning_trigger.value == DisableMousePositioningTrigger.ALL_FINGERS_FARAWAY_THUMB)):
            self.mouse_control.last_mouse_position = None
            return

        if (self.config.motion_border_left.value + self.config.motion_border_right.value < 1
                and self.config.motion_border_bottom.value + self.config.motion_border_top.value < 1):
            mouse_pos_px = self.get_mouse_position_px(hand_finger_positions.wrist_position.percent, frame)
            self.mouse_control.on_new_mouse_position_detected(mouse_pos_px)

    def get_mouse_position_px(self, screen_pos_percent: Vector, frame: Any) -> Vector:
        pos_percent_x = (screen_pos_percent.x - self.config.motion_border_left.value) / (1 - self.config.motion_border_left.value - self.config.motion_border_right.value)
        pos_percent_x = max(0, min(1, pos_percent_x))
        pos_percent_y = (screen_pos_percent.y - self.config.motion_border_top.value) / (1 - self.config.motion_border_top.value - self.config.motion_border_bottom.value)
        pos_percent_y = max(0, min(1, pos_percent_y))
        mouse_x = int(self.config.screen_offset.value.x + self.config.screen_size.value.x * pos_percent_x)
        mouse_y = int(self.config.screen_offset.value.y + self.config.screen_size.value.y * pos_percent_y)

        screen_pos_px = screen_pos_percent.scale(self.config.capture_size.value).add(Vector(10, 10))
        if self.config.mouse_positioning_mode.value == MousePositioningMode.ABSOLUTE:
            pos_text = f"{pos_percent_x * 100:.0f}% ({mouse_x}px) | {pos_percent_y * 100:.0f}% ({mouse_y}px)"
            put_text(frame, pos_text, screen_pos_px, 1.5, (255, 255, 255), 2)
        
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

    def detect_index_near_thumb_gesture(self,
                                        hand_finger_positions: HandFingerPositions) -> bool:
        index_finger_tip = hand_finger_positions.index_finger_positions[-1]
        thumb_finger_tip = hand_finger_positions.thumb_finger_positions[-1]
        middle_finger_tip = hand_finger_positions.middle_finger_positions[-1]
        ring_finger_tip = hand_finger_positions.ring_finger_positions[-1]
        pinky_finger_tip = hand_finger_positions.pinky_finger_positions[-1]

        is_only_index_near_thumb = (self.is_near_target([index_finger_tip], thumb_finger_tip)
                                    and self.is_faraway_target([middle_finger_tip, ring_finger_tip, pinky_finger_tip], thumb_finger_tip))
        self.index_near_thumb_flank_recognizer.set_value(is_only_index_near_thumb)

        return is_only_index_near_thumb

    def is_faraway_target(self,
            finger_positions: List[FingerPosition],
            target_position: FingerPosition) -> bool:
        finger_target_distances_percent = [Vector.distance_xy(finger_position.percent, target_position.percent) for finger_position in finger_positions]

        all_fingers_not_near_target = all(distance_percent > self.config.click_distance_threshold_high_percent.value
            for distance_percent in finger_target_distances_percent)

        return all_fingers_not_near_target

    def is_near_target(self,
            finger_positions: List[FingerPosition],
            target_position: FingerPosition) -> bool:
        finger_target_distances_percent = [Vector.distance_xy(finger_position.percent, target_position.percent) for finger_position in finger_positions]

        all_fingers_near_target = all(distance_percent < self.config.click_distance_threshold_low_percent.value
            for distance_percent in finger_target_distances_percent)

        return all_fingers_near_target

    def detect_middle_and_ring_near_thumb_gesture(self,
                                                  hand_finger_positions: HandFingerPositions) -> None:
        middle_finger_tip = hand_finger_positions.middle_finger_positions[-1]
        ring_finger_tip = hand_finger_positions.ring_finger_positions[-1]
        thumb_finger_tip = hand_finger_positions.thumb_finger_positions[-1]
        index_finger_tip = hand_finger_positions.index_finger_positions[-1]
        pinky_finger_tip = hand_finger_positions.pinky_finger_positions[-1]
        only_middle_and_ring_near_thumb = (self.is_near_target([middle_finger_tip, ring_finger_tip], thumb_finger_tip)
                                           and self.is_faraway_target([index_finger_tip, pinky_finger_tip], thumb_finger_tip))
        self.middle_and_ring_near_thumb_flank_recognizer.set_value(only_middle_and_ring_near_thumb)

    def detect_ring_and_pinky_near_thumb_gesture(self,
                                                 hand_finger_positions: HandFingerPositions) -> None:
        ring_finger_tip = hand_finger_positions.ring_finger_positions[-1]
        pinky_finger_tip = hand_finger_positions.pinky_finger_positions[-1]
        thumb_finger_tip = hand_finger_positions.thumb_finger_positions[-1]
        index_finger_tip = hand_finger_positions.index_finger_positions[-1]
        middle_finger_tip = hand_finger_positions.middle_finger_positions[-1]
        only_ring_and_pinky_near_thumb = (self.is_near_target([ring_finger_tip, pinky_finger_tip], thumb_finger_tip)
                                          and self.is_faraway_target([index_finger_tip, middle_finger_tip], thumb_finger_tip))
        self.ring_and_pinky_near_thumb_flank_recognizer.set_value(only_ring_and_pinky_near_thumb)

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

    def get_motion_border_top(self) -> float:
        if self.config.mouse_positioning_mode.value == MousePositioningMode.ABSOLUTE:
            return self.config.motion_border_top.value
        else:
            return 0

    def get_motion_border_left(self) -> float:
        if self.config.mouse_positioning_mode.value == MousePositioningMode.ABSOLUTE:
            return self.config.motion_border_left.value
        else:
            return 0

    def get_motion_border_right(self) -> float:
        if self.config.mouse_positioning_mode.value == MousePositioningMode.ABSOLUTE:
            return self.config.motion_border_right.value
        else:
            return 0

    def get_motion_border_bottom(self) -> float:
        if self.config.mouse_positioning_mode.value == MousePositioningMode.ABSOLUTE:
            return self.config.motion_border_bottom.value
        else:
            return 0

    def on_potential_left_click(self, current_time_ms: int) -> None:
        self.is_potential_left_click_gesture = True
        self.potential_left_click_start_time_ms = current_time_ms

    def on_left_click(self, current_time_ms: int) -> None:
        self.allow_left_click = False
        self.is_potential_left_click_gesture = False
        self.left_click_count = self.left_click_count + 1
        self.mouse_control.on_single_click_detected(MouseButton.LEFT)
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

    def on_drag_gesture_change(self, value: bool) -> None:
        if self.left_click_count == 1:
            if value:
                self.on_begin_drag()
            else:
                self.on_end_drag()

    def on_left_click_gesture_change(self, value: bool) -> None:
        if value and self.left_click_count == 0:
            current_time_ms = get_time_ms()
            self.on_left_click(current_time_ms)

    def on_right_click_gesture_change(self, value: bool) -> None:
        if value:
            current_time_ms = get_time_ms()
            self.on_right_click(current_time_ms)

    def on_middle_click_gesture_change(self, value: bool) -> None:
        if value:
            current_time_ms = get_time_ms()
            self.on_middle_click(current_time_ms)

    def on_index_near_thumb_rising_flank(self, value: bool) -> None:
        current_time_ms = get_time_ms()
        if (self.left_click_count < 2
                and current_time_ms < self.last_index_near_thumb_gesture_time_ms + self.config.double_click_max_pause_ms.value):
            self.on_double_left_click(current_time_ms)
        self.last_index_near_thumb_gesture_time_ms = current_time_ms

class ThumbGestureDirection(Enum):
    UP = 1
    DOWN = 2