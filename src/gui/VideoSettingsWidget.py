from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QFormLayout, QGroupBox, QSpinBox, QLabel, QLineEdit, QCheckBox
from common.Config import Config
from common.Config import VideoCaptureSource
from common.LogHolder import LogHolder
from common.Vector import Vector
from .MonitorSettingsWidget import MonitorDimensionSpinBox
from .RequireAppRestartLabel import RequireAppRestartLabel
from .qt_util import new_label

class VideoSettingsWidget(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        internal_webcam_widget = self.create_internal_webcam_widget()
        ip_webcam_widget = self.create_ip_webcam_widget()

        self.config.capture_source.subscribe_and_run(self.update_radio_buttons_by_capture_source)

        # Layout
        main_layout.addWidget(internal_webcam_widget)
        main_layout.addWidget(ip_webcam_widget)

    def update_config_by_internal_webcam_button(self) -> None:
        if self.internal_webcam_widget.isChecked():
            self.config.capture_source.value = VideoCaptureSource.INTEGRATED_WEBCAM

    def update_config_by_ip_webcam_button(self) -> None:
        if self.ip_webcam_widget.isChecked():
            self.config.capture_source.value = VideoCaptureSource.IP_WEBCAM

    def update_radio_buttons_by_capture_source(self, new_value: VideoCaptureSource) -> None:
        if (new_value == VideoCaptureSource.INTEGRATED_WEBCAM):
            self.internal_webcam_widget.setChecked(True)
            self.ip_webcam_widget.setChecked(False)
        elif (new_value == VideoCaptureSource.IP_WEBCAM):
            self.internal_webcam_widget.setChecked(False)
            self.ip_webcam_widget.setChecked(True)

    def add_capture_size_widgets(self, form_layout: QFormLayout) -> None:
        # Size
        self.capture_size_x_spinner = MonitorDimensionSpinBox()
        self.capture_size_y_spinner = MonitorDimensionSpinBox()
        form_layout.addRow(new_label("Width (Pixels)", "Horizontal size of the recorded video in pixels"),
                              self.capture_size_x_spinner)
        form_layout.addRow(new_label("Height (Pixels)", "Vertical size of the recorded video in pixels"),
                              self.capture_size_y_spinner)

        self.config.capture_size.subscribe_and_run(self.update_controls_of_capture_size)
        self.capture_size_x_spinner.valueChanged.connect(self.update_config_by_capture_size) # type: ignore
        self.capture_size_y_spinner.valueChanged.connect(self.update_config_by_capture_size) # type: ignore

        # FPS
        self.capture_fps_spinner = QSpinBox()
        form_layout.addRow(new_label("FPS", "The frames per second that are taken by the camera"),
                              self.capture_fps_spinner)

        self.capture_fps_spinner.setMaximum(200)
        self.capture_fps_spinner.setMinimum(5)
        self.config.capture_fps.subscribe_and_run(lambda new_value: self.capture_fps_spinner.setValue(new_value))
        self.capture_fps_spinner.valueChanged.connect(self.update_config_by_capture_fps)

    def update_controls_of_capture_size(self, new_capture_size: Vector) -> None:
        self.capture_size_x_spinner.setValue(int(new_capture_size.x))
        self.capture_size_y_spinner.setValue(int(new_capture_size.y))

    def update_config_by_capture_size(self) -> None:
        self.config.capture_size.value = Vector(self.capture_size_x_spinner.value(), self.capture_size_y_spinner.value())

    def update_config_by_capture_fps(self) -> None:
        self.config.capture_fps.value = self.capture_fps_spinner.value()

    def create_internal_webcam_widget(self) -> QWidget:
        internal_webcam_group = QGroupBox("Internal Webcam")
        internal_webcam_grid_layout = QGridLayout()
        internal_webcam_group.setLayout(internal_webcam_grid_layout)

        self.internal_webcam_widget = QCheckBox("Use Internal Webcam")
        self.internal_webcam_widget.setToolTip("Specifies that an integrated or otherwise connected (e.g. via USB) webcam should be used.")
        internal_webcam_grid_layout.addWidget(self.internal_webcam_widget)

        self.internal_webcam_widget.toggled.connect(self.update_config_by_internal_webcam_button)  # type: ignore

        # Capture size and FPS
        internal_webcam_form_layout = QFormLayout()
        internal_webcam_grid_layout.addLayout(internal_webcam_form_layout, 2, 0)
        self.add_capture_size_widgets(internal_webcam_form_layout)

        # Device number
        device_index_spinner = QSpinBox()
        internal_webcam_form_layout.addRow(new_label("Integrated Webcam Number",
                                                     "Specifies the webcam to use if multiple devices are available. First device is 0, second is 1, etc."),
                                           device_index_spinner)

        device_index_spinner.setMinimum(0)
        device_index_spinner.setMaximum(100)
        self.config.capture_device_index.subscribe_and_run(lambda new_value: device_index_spinner.setValue(new_value))
        device_index_spinner.valueChanged.connect(lambda new_value: self.config.capture_device_index.set_value(new_value))

        return internal_webcam_group

    def create_ip_webcam_widget(self) -> QWidget:
        ip_webcam_group = QGroupBox("IP Webcam")
        ip_webcam_grid_layout = QGridLayout()
        ip_webcam_group.setLayout(ip_webcam_grid_layout)

        self.ip_webcam_widget = QCheckBox("Use IP Camera")
        self.ip_webcam_widget.setToolTip("Specifies that a video stream from an IP camera should be used (e.g. from a smartphone).")
        ip_webcam_grid_layout.addWidget(self.ip_webcam_widget, 0, 0)

        self.ip_webcam_widget.toggled.connect(self.update_config_by_ip_webcam_button)  # type: ignore

        # IP Camera URL
        ip_camera_form_layout = QFormLayout()
        ip_webcam_grid_layout.addLayout(ip_camera_form_layout, 1, 0)
        self.ip_webcam_url_text_edit = QLineEdit()
        ip_camera_form_layout.addRow(new_label("URL",
                                               "URL to access the IP Camera's video stream.\nExpects a video stream in RTSP or MJPEG format or a JPG file."),
                                     self.ip_webcam_url_text_edit)

        self.config.capture_source_url.subscribe_and_run(lambda new_value: self.ip_webcam_url_text_edit.setText(new_value))
        self.ip_webcam_url_text_edit.editingFinished.connect(lambda: self.config.capture_source_url.set_value(self.ip_webcam_url_text_edit.text()))  # type: ignore

        return ip_webcam_group