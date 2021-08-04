from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QSpinBox, QWidget
from screeninfo.screeninfo import get_monitors

from Config import Config
from LogHolder import LogHolder
from Vector import Vector
from gui.qtutils import new_label
from util import to_json

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
        self.monitor_offset_x_spinner.valueChanged.connect(self.update_config_by_control)
        self.monitor_offset_y_spinner = MonitorOffsetSpinBox()
        self.monitor_offset_y_spinner.valueChanged.connect(self.update_config_by_control)
        self.main_layout.addRow(new_label("Offset X (Pixels)",
                                         "Sum of all monitor widths that are left of the target monitor"),
            self.monitor_offset_x_spinner)
        self.main_layout.addRow(new_label("Offset Y (Pixels)",
                                         "Sum of all monitor heights that are below the target monitor"),
            self.monitor_offset_y_spinner)

        # set initial checked state from config
        self.update_control_by_config()
        # update controls on config change
        Config.config_change_callbacks.append(self.update_control_by_config)

    def update_control_by_config(self) -> None:
        self.monitor_offset_x_spinner.setValue(int(self.config.screen_offset.value.x))
        self.monitor_offset_y_spinner.setValue(int(self.config.screen_offset.value.y))
        self.monitor_combo.setCurrentIndex(int(self.config.monitor_index.value))

    def update_config_by_control(self) -> None:
        last_config_json = to_json(self.config)
        self.config.screen_offset.value = Vector(self.monitor_offset_x_spinner.value(), self.monitor_offset_y_spinner.value())
        if (last_config_json != to_json(self.config)):
            Config.fire_config_changed_event()

class MonitorOffsetSpinBox(QSpinBox):
    def __init__(self) -> None:
        super().__init__()
        self.setMaximum(1000000)