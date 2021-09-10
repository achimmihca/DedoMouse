from __future__ import annotations
from typing import Any
from .Vector import Vector

class FingerPosition:
    def __init__(self, landmark: Any, capture_size: Vector) -> None:
        self.percent = Vector.from_xyz(landmark)
        self.px = self.percent.scale(capture_size).to_int_vector()