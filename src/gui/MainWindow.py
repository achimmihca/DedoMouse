#!/usr/bin/env python

from __future__ import annotations
from typing import Any
from PySide6.QtGui import QResizeEvent
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QLabel
from common.version import version
import common.AppContext as AppContext
from common.Config import VideoCaptureSource
from common.LogHolder import LogHolder
from common.Vector import Vector
from common.ReactiveProperty import ReactiveProperty
from .MainWidget import MainWidget
from .VideoCaptureThread import VideoCaptureThread
from rx import operators as ops

class MainWindow(QMainWindow, LogHolder):
    def __init__(self, app_context: AppContext.AppContext) -> None:
        QMainWindow.__init__(self)
        LogHolder.__init__(self)
        self.setWindowTitle(f"DedoMouse")
        self.app_context = app_context
        self.config = app_context.config

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

    def setup_video_capture(self) -> None:
        self.video_capture_thread = VideoCaptureThread(self.config, self.app_context.webcam_control, self.main_widget.image_label)
        self.video_capture_thread.start()

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

    def setup_status_bar(self) -> None:
        version_label = QLabel(f"Version: {version}")
        self.statusBar().addWidget(version_label)

        # Monitor size label
        monitor_size_label = QLabel()
        self.config.screen_size.subscribe_and_run(lambda new_value: monitor_size_label.setText(f"Monitor size: {new_value.x}x{new_value.y}"))
        self.statusBar().addWidget(monitor_size_label)

        # Capture size resp. IP webcam URL label
        self.video_settings_label = QLabel()
        self.config.capture_size.subscribe_and_run(self.update_video_settings_label)
        self.config.capture_fps.subscribe_and_run(self.update_video_settings_label)
        self.config.capture_source_url.subscribe_and_run(self.update_video_settings_label)
        self.statusBar().addWidget(self.video_settings_label)

        # Last performed action label
        self.last_performed_action_description = ""
        self.performed_action_description_count = 0
        self.performed_action_description_label = QLabel()
        self.statusBar().addWidget(self.performed_action_description_label)
        self.app_context.gesture_recognizer.jitter_pause_time_ms.subscribe(lambda new_value: self.update_performed_action_description_label(float(new_value), ""))
        self.app_context.mouse_control.performed_action_desciption.subscribe(lambda new_value: self.update_performed_action_description_label(0, new_value))

    def update_performed_action_description_label(self, new_jitter_pause_time_ms: float, performed_action_description: str) -> None:
        if (new_jitter_pause_time_ms <= 0):
            if (self.last_performed_action_description == performed_action_description):
                self.performed_action_description_count = self.performed_action_description_count + 1
            else:
                self.performed_action_description_count = 1
            performed_action_description_count_text = f" ({self.performed_action_description_count})" if self.performed_action_description_count > 1 else ""
            self.performed_action_description_label.setText(performed_action_description + performed_action_description_count_text)
            self.last_performed_action_description = performed_action_description
        else:
            self.performed_action_description_count = 0
            new_jitter_pause_time_seconds = new_jitter_pause_time_ms / 1000
            self.performed_action_description_label.setText(f"pause: {new_jitter_pause_time_seconds:.1} s")

    def update_video_settings_label(self, new_value: Any) -> None:
        if (self.config.capture_source.value == VideoCaptureSource.INTEGRATED_WEBCAM):
            w = self.app_context.webcam_control.actual_capture_size.x
            h = self.app_context.webcam_control.actual_capture_size.y
            fps = self.app_context.webcam_control.actual_fps
            self.video_settings_label.setText(f"Video: {w}x{h}@{fps}")
        else:
            self.video_settings_label.setText(f"Video: {self.config.capture_source_url.value}")

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
