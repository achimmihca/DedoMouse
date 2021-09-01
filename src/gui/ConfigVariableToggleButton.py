from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton, QSizePolicy
from typing import Any, List
from common.Config import Config
from common.LogHolder import LogHolder
from .ToggleButton import ToggleButton

class ConfigVariableToggleButton(ToggleButton, LogHolder):
    def __init__(self, config: Config, varname: str, image_path: str, tooltip: str, shortcuts: List[str]) -> None:
        ToggleButton.__init__(self, image_path, tooltip, shortcuts)
        LogHolder.__init__(self)
        self.config = config
        self.varname = varname.split("=")[0].replace("self.config.", "")

        # update config on checkbox state
        self.clicked.connect(self.update_config_value_by_toggle_button) # type: ignore
        # update checkbox on config change
        self.config.__dict__[self.varname].subscribe_and_run(self.update_toggle_button_by_config_value)

    def update_toggle_button_by_config_value(self, new_value: Any) -> None:
        if (new_value != self.isChecked()):
            self.setChecked(new_value)

    def update_config_value_by_toggle_button(self) -> None:
        if (self.config.__dict__[self.varname].value != self.isChecked()):
            self.config.__dict__[self.varname].value = self.isChecked()
