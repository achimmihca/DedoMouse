from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from common.Config import Config
from common.LogHolder import LogHolder
from .ConfigVariableCheckBox import ConfigVariableCheckBox

class EnabledMouseActionsTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.setLayout(QVBoxLayout())

        row1_layout = QHBoxLayout()
        self.layout().addLayout(row1_layout)
        row2_layout = QHBoxLayout()
        self.layout().addLayout(row2_layout)

        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_mouse_position=}", "Position"))
        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_click=}", "Click"))
        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_scroll=}", "Scroll"))

        row2_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_all_control_disabled=}", "Disable all"))
