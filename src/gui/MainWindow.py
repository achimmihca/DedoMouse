#!/usr/bin/env python

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QLabel

from Config import Config
from LogHolder import LogHolder
from WebcamControl import WebcamControl
from gui.MainWidget import MainWidget
from gui.VideoCaptureThread import VideoCaptureThread

class MainWindow(QMainWindow, LogHolder):
    def __init__(self, config: Config, webcam_control: WebcamControl) -> None:
        QMainWindow.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.webcam_control = webcam_control

        self.setup_style_sheet()
        self.setup_ui()
        self.setup_video_capture()

        self.log.info("init gui done")
        
    def setup_style_sheet(self) -> None:
        try:
            with open("styles.qss", mode="r", encoding="utf-8") as styles_file:
                styles_file_content = styles_file.read()
                self.setStyleSheet(styles_file_content)
        except Exception as e:
            self.log.error(f"Could not load style sheet: {str(e)}")

    def setup_ui(self) -> None:
        self.main_widget = MainWidget(self.config, self.close)
        self.setCentralWidget(self.main_widget)

        self.setup_status_bar()

        self.update_stay_on_top()
        Config.config_change_callbacks.append(self.update_stay_on_top)

    def setup_video_capture(self) -> None:
        self.video_capture_thread = VideoCaptureThread(self.config, self.webcam_control, self.main_widget.image_label)
        self.video_capture_thread.start()

    def setup_status_bar(self) -> None:
        capture_size_label = QLabel(f"Video size: {self.config.capture_size.x}x{self.config.capture_size.y}")
        self.statusBar().addWidget(capture_size_label)
        monitor_size_label = QLabel(f"Monitor size: {self.config.screen_size.x}x{self.config.screen_size.y}")
        self.statusBar().addWidget(monitor_size_label)

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

    def update_stay_on_top(self) -> None:
        last_window_flags = self.windowFlags()
        new_window_flags = self.windowFlags()
        if self.config.is_stay_on_top:
            new_window_flags = last_window_flags | Qt.WindowStaysOnTopHint
        else:
            new_window_flags = last_window_flags & ~Qt.WindowStaysOnTopHint
        if new_window_flags != last_window_flags:
            self.setWindowFlags(new_window_flags)
            self.show()
