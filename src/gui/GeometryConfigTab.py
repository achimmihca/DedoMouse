from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QFormLayout, QGroupBox
from common.Config import Config
from common.ReactiveProperty import ReactiveProperty
from common.LogHolder import LogHolder
from .qt_util import new_label

class GeometryConfigTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(self.create_motion_border_control())
        main_layout.addWidget(self.create_distance_threshold_control())

    def new_percent_slider(self, reactive_property: ReactiveProperty[float]) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)

        def update_control_by_config(new_value: int) -> None:
            reactive_property.value = float(new_value / 100)

        slider.valueChanged.connect(update_control_by_config)
        reactive_property.subscribe_and_run(lambda new_value: slider.setValue(int(new_value * 100)))
        return slider

    def create_motion_border_control(self) -> QWidget:
        left_slider = self.new_percent_slider(self.config.motion_border_left)
        right_slider = self.new_percent_slider(self.config.motion_border_right)
        top_slider = self.new_percent_slider(self.config.motion_border_top)
        bottom_slider = self.new_percent_slider(self.config.motion_border_bottom)

        def on_left_slider_changed() -> None:
            if (left_slider.value() > 100 - right_slider.value()):
                right_slider.setValue(100 - left_slider.value())

        def on_right_slider_changed() -> None:
            if (right_slider.value() > 100 - left_slider.value()):
                left_slider.setValue(100 - right_slider.value())

        def on_top_slider_changed() -> None:
            if (top_slider.value() > 100 - bottom_slider.value()):
                bottom_slider.setValue(100 - top_slider.value())

        def on_bottom_slider_changed() -> None:
            if (bottom_slider.value() > 100 - top_slider.value()):
                top_slider.setValue(100 - bottom_slider.value())

        left_slider.valueChanged.connect(on_left_slider_changed)
        right_slider.valueChanged.connect(on_right_slider_changed)
        top_slider.valueChanged.connect(on_top_slider_changed)
        bottom_slider.valueChanged.connect(on_bottom_slider_changed)

        group = QGroupBox("Positioning Border")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        form_layout = QFormLayout()
        group_layout.addLayout(form_layout)

        form_layout.addRow(new_label("Left", "Left border"), left_slider)
        form_layout.addRow(new_label("Right", "Right border"), right_slider)
        form_layout.addRow(new_label("Top", "Top border"), top_slider)
        form_layout.addRow(new_label("Bottom", "Bottom border"), bottom_slider)
        return group

    def create_distance_threshold_control(self) -> QWidget:
        distance_low_slider = self.new_percent_slider(self.config.click_distance_threshold_low_percent)
        distance_high_slider = self.new_percent_slider(self.config.click_distance_threshold_high_percent)

        def on_low_slider_changed() -> None:
            if (distance_low_slider.value() > distance_high_slider.value()):
                distance_high_slider.setValue(distance_low_slider.value())

        def on_high_slider_changed() -> None:
            if (distance_high_slider.value() < distance_low_slider.value()):
                distance_low_slider.setValue(distance_high_slider.value())

        distance_low_slider.valueChanged.connect(on_low_slider_changed)
        distance_high_slider.valueChanged.connect(on_high_slider_changed)

        group = QGroupBox("Distance Threshold")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        form_layout = QFormLayout()
        group_layout.addLayout(form_layout)

        form_layout.addRow(new_label("Low", "Low distance threshold"), distance_low_slider)
        form_layout.addRow(new_label("High", "High distance threshold"), distance_high_slider)
        return group
