#!/usr/bin/env python

from typing import Any, Callable
import logging
from PySide6.QtCore import QThread, QSize, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QCheckBox, QGridLayout, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout
import cv2 # type: ignore

from Config import Config
from WebcamControl import WebcamControl
 
class MainQtWindow(QMainWindow):
    def __init__(self, config: Config, webcam_control: WebcamControl) -> None:
        QMainWindow.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
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
        self.video_capture_thread = VideoCaptureThread(self, self.webcam_control, self.main_widget.image_label)
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

class MainWidget(QWidget):
    def __init__(self, config: Config, close_callback: Callable) -> None:
        QWidget.__init__(self)
        self.config = config
        self.close_callback = close_callback
        self.setup_ui()

    def setup_ui(self) -> None:
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.image_label = QLabel("Starting Camera...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(QSize(int(320), int(240)))
        self.main_layout.addWidget(self.image_label)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_callback)
        self.main_layout.addWidget(self.quit_button)

        self.setup_controls()

    def setup_controls(self) -> None:
        checkbox_grid_layout = QGridLayout()
        self.main_layout.addLayout(checkbox_grid_layout)
        checkbox_count = 0
        def add_checkbox_for_config_var(varname: str, label_name: str) -> None:
            nonlocal checkbox_count
            nonlocal checkbox_grid_layout
            varname = varname.split("=")[0].replace("self.config.", "")
            checkbox = QCheckBox(label_name)
            row = int(checkbox_count / 3)
            column = int(checkbox_count % 3)
            checkbox_grid_layout.addWidget(checkbox, row, column)
            checkbox_count = checkbox_count + 1

            def update_checkbox_by_config_value() -> None:
                varvalue = self.config.__dict__[varname]
                if (varvalue != checkbox.isChecked()):
                    checkbox.setChecked(varvalue)

            def update_config_value_by_checkbox() -> None:
                self.config.__dict__[varname] = checkbox.isChecked()
                Config.fire_config_changed_event()
                self.log.info(f"set {varname} to {self.config.__dict__[varname]}")

            # set initial checked state from config
            update_checkbox_by_config_value()
            # update config on checkbox state
            checkbox.stateChanged.connect(update_config_value_by_checkbox)
            # update checkbox on config change
            Config.config_change_callbacks.append(update_checkbox_by_config_value)

        add_checkbox_for_config_var(f"{self.config.is_control_mouse_position=}", "Control mouse position")
        add_checkbox_for_config_var(f"{self.config.is_control_click=}", "Control click")
        add_checkbox_for_config_var(f"{self.config.is_control_scroll=}", "Control scroll")
        add_checkbox_for_config_var(f"{self.config.is_all_control_disabled=}", "Disable all controls")
        add_checkbox_for_config_var(f"{self.config.is_trigger_additional_click_on_double_click=}", "Trigger additional click on double-click")
        add_checkbox_for_config_var(f"{self.config.is_stay_on_top=}", "Stay on top")

class VideoCaptureThread(QThread):
    def __init__(self, main_gui: MainQtWindow, webcam_control: WebcamControl, video_display_label: QLabel) -> None:
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