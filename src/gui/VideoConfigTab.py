from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QSpinBox, QLabel
from common.Config import Config
from common.LogHolder import LogHolder
from common.Vector import Vector
from .MonitorConfigTab import MonitorDimensionSpinBox
from .qt_util import new_label

class VideoConfigTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.create_capture_size_group())

        # Warning label
        label = QLabel("Parameters of this tab require a restart")
        label.setAlignment(Qt.AlignCenter)
        label.setProperty("cssClass", "highlight") # type: ignore
        self.layout().addWidget(label)


    def create_capture_size_group(self) -> QWidget:
        group = QGroupBox("Capture Size")
        group.setLayout(QFormLayout())

        # Size
        self.capture_size_x_spinner = MonitorDimensionSpinBox()
        self.capture_size_y_spinner = MonitorDimensionSpinBox()
        group.layout().addRow(new_label("Size X (Pixels)", "Horizontal size of the recorded video in pixels"),
                              self.capture_size_x_spinner)
        group.layout().addRow(new_label("Size Y (Pixels)", "Vertical size of the recorded video in pixels"),
                              self.capture_size_y_spinner)

        self.config.capture_size.subscribe_and_run(self.update_controls_of_capture_size)
        self.capture_size_x_spinner.valueChanged.connect(self.update_config_by_capture_size)
        self.capture_size_y_spinner.valueChanged.connect(self.update_config_by_capture_size)

        # FPS
        self.capture_fps_spinner = QSpinBox()
        group.layout().addRow(new_label("FPS", "The frames per second that are taken by the camera"),
                              self.capture_fps_spinner)

        self.capture_fps_spinner.setMaximum(200)
        self.capture_fps_spinner.setMinimum(5)
        self.config.capture_fps.subscribe_and_run(lambda new_value: self.capture_fps_spinner.setValue(new_value))
        self.capture_fps_spinner.valueChanged.connect(self.update_config_by_capture_fps)

        return group

    def update_controls_of_capture_size(self, new_capture_size: Vector) -> None:
        self.capture_size_x_spinner.setValue(int(new_capture_size.x))
        self.capture_size_y_spinner.setValue(int(new_capture_size.y))

    def update_config_by_capture_size(self) -> None:
        self.config.capture_size.value = Vector(self.capture_size_x_spinner.value(), self.capture_size_y_spinner.value())

    def update_config_by_capture_fps(self) -> None:
        self.config.capture_fps.value = self.capture_fps_spinner.value()
