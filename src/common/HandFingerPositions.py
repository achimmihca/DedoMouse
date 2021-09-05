from __future__ import annotations
from typing import Any, List
from itertools import chain
import mediapipe # type: ignore
from .Vector import Vector
from .FingerPosition import FingerPosition
import common.GestureRecognizer as GestureRecognizer

class HandFingerPositions:
    def __init__(self, single_hand_landmarks: Any, capture_size: Vector) -> None:
        self.single_hand_landmarks = single_hand_landmarks

        self.wrist_position = FingerPosition(single_hand_landmarks.landmark[GestureRecognizer.GestureRecognizer.wrist_index], capture_size)
        self.thumb_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.GestureRecognizer.thumb_finger_indexes, capture_size)
        self.index_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.GestureRecognizer.index_finger_indexes, capture_size)
        self.middle_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.GestureRecognizer.middle_finger_indexes, capture_size)
        self.ring_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.GestureRecognizer.ring_finger_indexes, capture_size)
        self.pinky_finger_positions = self.get_finger_positions_from_hand_landmarks(GestureRecognizer.GestureRecognizer.pinky_finger_indexes, capture_size)

        self.thumb_tip_position = self.thumb_finger_positions[-1]
        self.index_tip_position = self.index_finger_positions[-1]
        self.middle_tip_position = self.middle_finger_positions[-1]
        self.ring_tip_position = self.ring_finger_positions[-1]
        self.pinky_tip_position = self.pinky_finger_positions[-1]

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
