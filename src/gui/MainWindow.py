#!/usr/bin/env python

from typing import Any
from PySide6.QtGui import QResizeEvent
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QLabel
from common.version import version
from common.Config import Config
from common.LogHolder import LogHolder
from common.WebcamControl import WebcamControl
from common.Vector import Vector
from common.ReactiveProperty import ReactiveProperty
from .MainWidget import MainWidget
from .VideoCaptureThread import VideoCaptureThread
from rx import operators as ops

class MainWindow(QMainWindow, LogHolder):
    def __init__(self, config: Config, webcam_control: WebcamControl) -> None:
        QMainWindow.__init__(self)
        LogHolder.__init__(self)
        self.setWindowTitle(f"DedoMouse")
        self.config = config
        self.webcam_control = webcam_control

        self.setup_style_sheet()
        self.setup_ui()
        self.setup_video_capture()

        self.log.info("init gui done")

        self.resize(int(self.config.window_size.value.x), int(self.config.window_size.value.y))

        # Resize event as observable
        self.resize_event_reactive_property = ReactiveProperty(Vector(self.config.window_size.value.x, self.config.window_size.value.y))

        # Only write stable values to the config by using rx.debounce
        def update_config_window_size(new_value: Vector) -> None:
            self.config.window_size.value = new_value
        self.resize_event_reactive_property.pipe(ops.debounce(0.1)).subscribe(update_config_window_size)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if hasattr(self, 'resize_event_reactive_property'):
            self.resize_event_reactive_property.value = Vector(event.size().width(), event.size().height())

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

        self.config.is_stay_on_top.subscribe_and_run(self.update_stay_on_top)

    def setup_video_capture(self) -> None:
        self.video_capture_thread = VideoCaptureThread(self.config, self.webcam_control, self.main_widget.image_label)
        self.video_capture_thread.start()

    def setup_status_bar(self) -> None:
        global version
        version_label = QLabel(f"Version: {version}")
        self.statusBar().addWidget(version_label)

        self.capture_size_label = QLabel()
        self.config.capture_size.subscribe_and_run(self.update_capture_size_label)
        self.config.capture_fps.subscribe_and_run(self.update_capture_size_label)
        self.statusBar().addWidget(self.capture_size_label)

        monitor_size_label = QLabel()
        self.config.screen_size.subscribe_and_run(lambda new_value: monitor_size_label.setText(f"Monitor size: {new_value.x}x{new_value.y}"))
        self.statusBar().addWidget(monitor_size_label)

    def update_capture_size_label(self, new_value: Any) -> None:
        self.capture_size_label.setText(f"Video: {self.webcam_control.actual_capture_size.x}x{self.webcam_control.actual_capture_size.y}@{self.webcam_control.fps}")

    def closeEvent(self, event: Any) -> None:
        self.log.info("shutting down app")

        self.config.save_to_file()

        # Stop main loop of video capture thread
        self.config.running.value = False
        self.log.info("waiting for video capture thread to terminate")
        self.video_capture_thread.wait()
        # Close Qt application
        self.close()

        self.log.info("DedoMouse finished")

    def update_stay_on_top(self, new_stay_on_top: bool) -> None:
        last_window_flags = self.windowFlags()
        # noinspection PyUnusedLocal
        new_window_flags = self.windowFlags()
        if new_stay_on_top:
            new_window_flags = last_window_flags | Qt.WindowStaysOnTopHint
        else:
            new_window_flags = last_window_flags & ~Qt.WindowStaysOnTopHint # type: ignore

        if new_window_flags != last_window_flags:
            self.setWindowFlags(new_window_flags)
            self.show()
