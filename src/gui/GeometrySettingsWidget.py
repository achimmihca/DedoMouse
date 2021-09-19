from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QFormLayout, QGroupBox, QRadioButton
from common.Config import Config
from common.Config import MousePositioningMode
from common.Config import DisableMousePositioningTrigger
from common.ReactiveProperty import ReactiveProperty
from common.LogHolder import LogHolder
from common.Vector import Vector
from .MonitorSettingsWidget import MonitorDimensionSpinBox
from .qt_util import new_label

class GeometrySettingsWidget(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(self.create_mouse_positioning_control())

        mouse_position_difference_control = self.create_mouse_position_difference_control()
        main_layout.addWidget(mouse_position_difference_control)

        motion_border_control = self.create_motion_border_control()
        main_layout.addWidget(motion_border_control)

        monitor_offset_group = self.create_monitor_offset_group()
        main_layout.addWidget(monitor_offset_group)

        main_layout.addWidget(self.create_disable_mouse_positioning_trigger_control())
        main_layout.addWidget(self.create_distance_threshold_control())

        self.config.mouse_positioning_mode.subscribe_and_run(lambda new_value: mouse_position_difference_control.setVisible(new_value == MousePositioningMode.RELATIVE))
        self.config.mouse_positioning_mode.subscribe_and_run(lambda new_value: motion_border_control.setVisible(new_value == MousePositioningMode.ABSOLUTE))
        self.config.mouse_positioning_mode.subscribe_and_run(lambda new_value: monitor_offset_group.setVisible(new_value == MousePositioningMode.ABSOLUTE))

    def new_percent_slider(self, reactive_property: ReactiveProperty[float], slider_min: int = 0, slider_max: int = 100) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(slider_min)
        slider.setMaximum(slider_max)

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

        group = QGroupBox("Absolute Positioning Border")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        form_layout = QFormLayout()
        group_layout.addLayout(form_layout)

        form_layout.addRow(new_label("Left", "Left border"), left_slider)
        form_layout.addRow(new_label("Right", "Right border"), right_slider)
        form_layout.addRow(new_label("Top", "Top border"), top_slider)
        form_layout.addRow(new_label("Bottom", "Bottom border"), bottom_slider)
        return group

    def create_mouse_positioning_control(self) -> QWidget:
        group = QGroupBox("Positioning Mode")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        relative_positioning_radio = QRadioButton("Relative")
        absolute_positioning_radio = QRadioButton("Absolute")

        def update_positioning_radio_by_config_value(new_value: MousePositioningMode) -> None:
            if new_value == MousePositioningMode.RELATIVE:
                relative_positioning_radio.setChecked(True)
            elif new_value == MousePositioningMode.ABSOLUTE:
                absolute_positioning_radio.setChecked(True)

        self.config.mouse_positioning_mode.subscribe_and_run(update_positioning_radio_by_config_value)
        relative_positioning_radio.clicked.connect(lambda new_value: self.config.mouse_positioning_mode.set_value(MousePositioningMode.RELATIVE))
        absolute_positioning_radio.clicked.connect(lambda new_value: self.config.mouse_positioning_mode.set_value(MousePositioningMode.ABSOLUTE))

        group_layout.addWidget(relative_positioning_radio)
        group_layout.addWidget(absolute_positioning_radio)

        return group

    def create_disable_mouse_positioning_trigger_control(self) -> QWidget:
        group = QGroupBox("Disable Positioning When")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        all_near_thumb_radio = QRadioButton("All fingers near thumb")
        all_faraway_thumb_radio = QRadioButton("All fingers faraway from thumb")
        any_faraway_thumb_radio = QRadioButton("Any finger faraway from thumb")

        def update_trigger_radio_by_config_value(new_value: DisableMousePositioningTrigger) -> None:
            if new_value == DisableMousePositioningTrigger.ALL_FINGERS_NEAR_THUMB:
                all_near_thumb_radio.setChecked(True)
            elif new_value == DisableMousePositioningTrigger.ALL_FINGERS_FARAWAY_THUMB:
                all_faraway_thumb_radio.setChecked(True)
            elif new_value == DisableMousePositioningTrigger.ANY_FINGER_FARAWAY_THUMB:
                any_faraway_thumb_radio.setChecked(True)

        self.config.disable_mouse_positioning_trigger.subscribe_and_run(update_trigger_radio_by_config_value)
        all_near_thumb_radio.clicked.connect(lambda new_value: self.config.disable_mouse_positioning_trigger.set_value(DisableMousePositioningTrigger.ALL_FINGERS_NEAR_THUMB))
        all_faraway_thumb_radio.clicked.connect(lambda new_value: self.config.disable_mouse_positioning_trigger.set_value(DisableMousePositioningTrigger.ALL_FINGERS_FARAWAY_THUMB))
        any_faraway_thumb_radio.clicked.connect(lambda new_value: self.config.disable_mouse_positioning_trigger.set_value(DisableMousePositioningTrigger.ANY_FINGER_FARAWAY_THUMB))

        group_layout.addWidget(all_near_thumb_radio)
        group_layout.addWidget(all_faraway_thumb_radio)
        group_layout.addWidget(any_faraway_thumb_radio)

        return group

    def create_mouse_position_difference_control(self) -> QWidget:
        difference_sensitivity = self.new_percent_slider(self.config.mouse_position_difference_sensitivity, 10, 200)

        group = QGroupBox("Relative Positioning Sensitivity")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        form_layout = QFormLayout()
        group_layout.addLayout(form_layout)

        form_layout.addRow(new_label("Sensitivity", "Position difference sensitivity"), difference_sensitivity)
        return group

    def create_distance_threshold_control(self) -> QWidget:
        distance_low_slider = self.new_percent_slider(self.config.click_distance_threshold_low_percent, 1, 50)
        distance_high_slider = self.new_percent_slider(self.config.click_distance_threshold_high_percent, 1, 50)

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

        distance_tooltip = "Move fingers from high-distance to low-distance to trigger a click."
        form_layout.addRow(new_label("Low", distance_tooltip), distance_low_slider)
        form_layout.addRow(new_label("High", distance_tooltip), distance_high_slider)
        return group

    def create_monitor_offset_group(self) -> QWidget:
        group = QGroupBox("Absolute Positioning Offset")
        form_layout = QFormLayout()
        group.setLayout(form_layout)

        self.monitor_offset_x_spinner = MonitorDimensionSpinBox()
        self.monitor_offset_y_spinner = MonitorDimensionSpinBox()
        form_layout.addRow(new_label("Offset X (Pixels)", "Sum of all monitor widths that are left of the target monitor"),
                              self.monitor_offset_x_spinner)
        form_layout.addRow(new_label("Offset Y (Pixels)", "Sum of all monitor heights that are below the target monitor"),
                              self.monitor_offset_y_spinner)

        self.config.screen_offset.subscribe_and_run(self.update_controls_of_screen_offset)
        self.monitor_offset_x_spinner.valueChanged.connect(self.update_config_by_screen_offset)
        self.monitor_offset_y_spinner.valueChanged.connect(self.update_config_by_screen_offset)

        return group

    def update_controls_of_screen_offset(self, new_screen_offset: Vector) -> None:
        self.monitor_offset_x_spinner.setValue(int(new_screen_offset.x))
        self.monitor_offset_y_spinner.setValue(int(new_screen_offset.y))

    def update_config_by_screen_offset(self) -> None:
        self.config.screen_offset.value = Vector(self.monitor_offset_x_spinner.value(), self.monitor_offset_y_spinner.value())