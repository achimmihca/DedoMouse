from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox
from common.Config import Config
from common.LogHolder import LogHolder
from .ConfigVariableCheckBox import ConfigVariableCheckBox

class EnabledMouseActionsTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.setLayout(QVBoxLayout())

        self.layout().addWidget(self.create_enabled_mouse_action_controls())
        self.layout().addWidget(self.create_other_controls())

    def create_enabled_mouse_action_controls(self) -> QWidget:
        group = QGroupBox("Mouse Control")
        group.setLayout(QVBoxLayout())

        row1_layout = QHBoxLayout()
        group.layout().addLayout(row1_layout)
        row2_layout = QHBoxLayout()
        group.layout().addLayout(row2_layout)

        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_mouse_position=}", "Position"))
        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_click=}", "Click"))
        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_scroll=}", "Scroll"))

        row2_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_all_control_disabled=}", "Disable all"))

        return group

    def create_other_controls(self) -> QWidget:
        group = QGroupBox("Misc.")
        group.setLayout(QVBoxLayout())

        group.layout().addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_stay_on_top=}", "Stay on top"))

        return group