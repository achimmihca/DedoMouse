from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QSpinBox, QWidget
from screeninfo import get_monitors

from common.Config import Config
from common.LogHolder import LogHolder
from common.Vector import Vector
from .qtutils import new_label

class MonitorConfigControl(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config

        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)

        # Monitor selection control
        self.monitor_combo = QComboBox()
        self.main_layout.addRow(new_label("Target Monitor",
                                         "The monitor on which the mouse will be positioned"),
            self.monitor_combo)
        monitors = get_monitors()
        for index, monitor in enumerate(monitors):
            self.monitor_combo.addItem(monitor.name, index)

        self.monitor_offset_layout = QHBoxLayout()

        # Offset controls
        self.monitor_offset_x_spinner = MonitorOffsetSpinBox()
        self.monitor_offset_y_spinner = MonitorOffsetSpinBox()
        self.main_layout.addRow(new_label("Offset X (Pixels)",
                                          "Sum of all monitor widths that are left of the target monitor"),
            self.monitor_offset_x_spinner)
        self.main_layout.addRow(new_label("Offset Y (Pixels)",
                                          "Sum of all monitor heights that are below the target monitor"),
            self.monitor_offset_y_spinner)

        # update controls on config change
        self.config.screen_offset.subscribe_and_run(self.update_controls_of_screen_offset)
        self.config.monitor_index.subscribe_and_run(self.update_controls_of_monitor_index)

        # update config on control change
        self.monitor_offset_x_spinner.valueChanged.connect(self.update_config_by_screen_offset)
        self.monitor_offset_y_spinner.valueChanged.connect(self.update_config_by_screen_offset)
        self.monitor_combo.currentIndexChanged.connect(self.update_config_by_monitor_index)

    def update_controls_of_monitor_index(self, new_monitor_index: int) -> None:
        self.monitor_combo.setCurrentIndex(new_monitor_index)

    def update_controls_of_screen_offset(self, new_screen_offset: Vector) -> None:
        self.monitor_offset_x_spinner.setValue(int(new_screen_offset.x))
        self.monitor_offset_y_spinner.setValue(int(new_screen_offset.y))

    def update_config_by_screen_offset(self) -> None:
        self.config.screen_offset.value = Vector(self.monitor_offset_x_spinner.value(), self.monitor_offset_y_spinner.value())

    def update_config_by_monitor_index(self) -> None:
        self.config.monitor_index.value = self.monitor_combo.currentIndex()

class MonitorOffsetSpinBox(QSpinBox):
    def __init__(self) -> None:
        super().__init__()
        self.setMaximum(1000000)