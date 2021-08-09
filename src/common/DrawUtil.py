from typing import Any, Tuple
from cv2 import cv2
from .Vector import Vector

def draw_circle(frame: Any, position: Vector, color_rgb: Tuple[int, int, int]) -> None:
    cv2.circle(frame, position.to_tuple_2(), 5, color_rgb, -1)   
    