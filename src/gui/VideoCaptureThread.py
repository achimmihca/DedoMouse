#!/usr/bin/env python

from typing import Any
import logging
import cv2
from PySide6.QtCore import QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel
from common.Config import Config
from common.Vector import Vector

from common.WebcamControl import WebcamControl

class VideoCaptureThread(QThread):
    def __init__(self, config: Config, webcam_control: WebcamControl, video_display_label: QLabel) -> None:
        QThread.__init__(self)
        self.config = config
        self.webcam_control = webcam_control
        self.video_display_label = video_display_label
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self) -> None:
        self.log.info("started VideoCaptureThread")
        self.webcam_control.frame_analyzed_callbacks.append(self.display_video_frame)
        try:
            video_capture_error_message = self.webcam_control.start_video_capture()
            if video_capture_error_message is not None:
                self.video_display_label.setText(video_capture_error_message)
        except Exception:
            error_message = ":(\n\nError during video capture or processing.\nCheck log file for further information."
            self.log.exception(error_message)
            self.video_display_label.setText(error_message)

    def display_video_frame(self, frame: Any, frame_size: Vector) -> None:
        try:
            label_width = self.video_display_label.width()
            label_height = self.video_display_label.height()
            scale_x = label_width / frame_size.x
            scale_y = label_height / frame_size.y
            scale = min(scale_x, scale_y)
            frame = cv2.resize(frame, None, fx=scale, fy=scale)
            image = QImage(frame, frame.shape[1], frame.shape[0],
                        frame.strides[0], QImage.Format_RGB888)
            self.video_display_label.setPixmap(QPixmap.fromImage(image))
        except Exception:
            self.log.exception(f"Could not display video.")
