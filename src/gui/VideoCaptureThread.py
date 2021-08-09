#!/usr/bin/env python

from typing import Any
import logging
import cv2
from PySide6.QtCore import QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel
from common.Config import Config # type: ignore

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
        self.webcam_control.start_video_capture()

    def display_video_frame(self, frame: Any) -> None:
        try:
            label_width = self.video_display_label.width()
            label_height = self.video_display_label.height()
            scale_x = label_width / self.config.capture_size.value.x
            scale_y = label_height / self.config.capture_size.value.y
            scale = min(scale_x, scale_y)
            frame = cv2.resize(frame, None, fx=scale, fy=scale)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], 
                        frame.strides[0], QImage.Format_RGB888)
            self.video_display_label.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            self.log.error(f"Could not display video: {str(e)}")