from PySide6.QtWidgets import QWidget, QVBoxLayout
from common.Config import Config
from common.LogHolder import LogHolder
from .ConfigVariableCheckBox import ConfigVariableCheckBox

class OtherConfigTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_trigger_additional_click_on_double_click=}", "Trigger additional click on double-click"))
        self.layout().addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_stay_on_top=}", "Stay on top"))