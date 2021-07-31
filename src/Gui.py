#!/usr/bin/env python

from typing import Any
import time
import logging
from PySide6.QtCore import QThread, QSize, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QSizePolicy, QWidget, QLabel, QPushButton, QVBoxLayout
import cv2 # type: ignore

from Config import Config
from WebcamControl import WebcamControl

class MainGui(QWidget):
    def __init__(self, config: Config, webcam_control: WebcamControl) -> None:
        QWidget.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.webcam_control = webcam_control
        self.setup_ui()
        self.video_capture_thread = VideoCaptureThread(self, self.webcam_control, self.image_label)
        self.video_capture_thread.start()
        time.sleep(3)
        self.log.info("init gui done")

    def setup_ui(self) -> None:
        self.image_label = QLabel()
        #self.image_label.setSizePolicy(QSizePolicy(QSizePolicy.Minimum))
        self.image_label.setMinimumSize(QSize(int(320), int(240)))

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.quit_button)

        self.setLayout(self.main_layout)

    def closeEvent(self, event: Any) -> None:
        self.log.info("shutting down app")

        self.config.save_to_file()

        # Stop main loop of video capture thread
        self.config.running = False
        self.log.info("waiting for video capture thread to terminate")
        self.video_capture_thread.wait()
        # Close Qt application
        self.close()

        self.log.info("DedoMouse finished")

class VideoCaptureThread(QThread):
    def __init__(self, main_gui: MainGui, webcam_control: WebcamControl, video_display_label: QLabel) -> None:
        QThread.__init__(self)
        self.main_gui = main_gui
        self.webcam_control = webcam_control
        self.video_display_label = video_display_label
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self) -> None:
        self.log.info("started VideoCaptureThread")
        self.webcam_control.frame_analyzed_callbacks.append(self.display_video_frame)
        self.webcam_control.start_video_capture()

    def display_video_frame(self, frame: Any) -> None:
        label_width = self.video_display_label.width()
        label_height = self.video_display_label.height()
        scale_x = label_width / self.main_gui.config.capture_size.x
        scale_y = label_height / self.main_gui.config.capture_size.y
        scale = min(scale_x, scale_y)
        frame = cv2.resize(frame, None, fx=scale, fy=scale)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], 
                       frame.strides[0], QImage.Format_RGB888)
        self.video_display_label.setPixmap(QPixmap.fromImage(image))