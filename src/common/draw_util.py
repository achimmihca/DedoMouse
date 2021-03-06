from typing import Any, Tuple
from cv2 import cv2
from .Vector import Vector

def draw_line(frame: Any, pos1: Vector, pos2: Vector, color_rgb: Tuple[int, int, int], thickness: int=None) -> None:
    cv2.line(frame, pos1.to_int_vector().to_tuple_2(), pos2.to_int_vector().to_tuple_2(), color_rgb, thickness)

def draw_circle(frame: Any, position: Vector, radius: float, color_rgb: Tuple[int, int, int], thickness: int=-1) -> None:
    cv2.circle(frame, position.to_int_vector().to_tuple_2(), int(radius), color_rgb, thickness)

def put_text(frame: Any, text: str, position: Vector, font_scale: float, color_rgb: Tuple[int, int, int], thickness: int=None) -> None:
    cv2.putText(frame, text, position.to_int_vector().to_tuple_2(), cv2.FONT_HERSHEY_PLAIN, font_scale, color_rgb, thickness)

def to_bgr(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (rgb[2], rgb[1], rgb[0])