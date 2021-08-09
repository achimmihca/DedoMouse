from PySide6.QtWidgets import QCheckBox
from typing import Any
from common.Config import Config
from common.LogHolder import LogHolder

class ConfigVariableCheckBox(QCheckBox, LogHolder):
    def __init__(self, config: Config, varname: str, label_name: str) -> None:
        QCheckBox.__init__(self, label_name)
        LogHolder.__init__(self)
        self.config = config
        self.varname = varname.split("=")[0].replace("self.config.", "")
        self.label_name = label_name

        # update config on checkbox state
        self.stateChanged.connect(self.update_config_value_by_checkbox)
        # update checkbox on config change
        self.config.__dict__[self.varname].subscribe_and_run(self.update_checkbox_by_config_value)

    def update_checkbox_by_config_value(self, new_value: Any) -> None:
        if (new_value != self.isChecked()):
            self.setChecked(new_value)

    def update_config_value_by_checkbox(self) -> None:
        if (self.config.__dict__[self.varname].value != self.isChecked()):
            self.config.__dict__[self.varname].value = self.isChecked()
