from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from common.Config import Config
from .ConfigVariableCheckBox import ConfigVariableCheckBox

class EnabledMouseActionsControl(QWidget):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        row1_layout = QHBoxLayout()
        self.main_layout.addLayout(row1_layout)
        row2_layout = QHBoxLayout()
        self.main_layout.addLayout(row2_layout)
        
        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_mouse_position=}", "Position"))
        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_click=}", "Click"))
        row1_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_scroll=}", "Scroll"))

        row2_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_all_control_disabled=}", "Disable all"))
