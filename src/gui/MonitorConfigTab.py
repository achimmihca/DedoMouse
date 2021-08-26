from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QSpinBox, QGroupBox, QGridLayout
from common.Config import Config
from common.LogHolder import LogHolder
from common.Vector import Vector
from screeninfo import get_monitors
from .qt_util import new_label

class MonitorConfigTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.create_monitor_size_group())
        self.layout().addWidget(self.create_monitor_offset_group())

    def create_monitor_size_group(self) -> QWidget:
        group = QGroupBox("Monitor Size")
        form_layout = QFormLayout()
        group.setLayout(form_layout)

        # Monitor selection control
        self.monitor_combo = QComboBox()
        form_layout.addRow(new_label("Target Monitor", "The monitor on which the mouse will be positioned"),
                           self.monitor_combo)

        monitors = get_monitors()
        for index, monitor in enumerate(monitors):
            self.monitor_combo.addItem(monitor.name, index)

        self.config.monitor_index.subscribe_and_run(lambda new_value: self.monitor_combo.setCurrentIndex(new_value))
        self.monitor_combo.currentIndexChanged.connect(self.update_config_by_monitor_index)

        # Size selection controls
        self.monitor_size_x_spinner = MonitorDimensionSpinBox()
        form_layout.addRow(new_label("Width (Pixels)", "Horizontal size of the monitor in pixels"),
                           self.monitor_size_x_spinner)
        self.monitor_size_y_spinner = MonitorDimensionSpinBox()
        form_layout.addRow(new_label("Height (Pixels)", "Vertical size of the monitor in pixels"),
                           self.monitor_size_y_spinner)

        self.config.screen_size.subscribe_and_run(self.update_controls_of_screen_size)
        self.monitor_size_x_spinner.valueChanged.connect(self.update_config_by_screen_size)
        self.monitor_size_y_spinner.valueChanged.connect(self.update_config_by_screen_size)

        return group

    def create_monitor_offset_group(self) -> QWidget:
        group = QGroupBox("Monitor Offset")
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

    def update_controls_of_screen_size(self, new_screen_size: Vector) -> None:
        self.monitor_size_x_spinner.setValue(int(new_screen_size.x))
        self.monitor_size_y_spinner.setValue(int(new_screen_size.y))

    def update_config_by_screen_size(self) -> None:
        self.config.screen_size.value = Vector(self.monitor_size_x_spinner.value(), self.monitor_size_y_spinner.value())

    def update_config_by_monitor_index(self) -> None:
        self.config.monitor_index.value = self.monitor_combo.currentIndex()
        self.config.update_screen_size()

class MonitorDimensionSpinBox(QSpinBox):
    def __init__(self) -> None:
        QSpinBox.__init__(self)
        self.setMaximum(1000000)