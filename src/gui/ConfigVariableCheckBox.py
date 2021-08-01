from PySide6.QtWidgets import QCheckBox

from Config import Config
from LogHolder import LogHolder

class ConfigVariableCheckBox(QCheckBox, LogHolder):
    def __init__(self, config: Config, varname: str, label_name: str) -> None:
        QCheckBox.__init__(self, label_name)
        LogHolder.__init__(self)
        self.config = config
        self.varname = varname.split("=")[0].replace("self.config.", "")
        self.label_name = label_name

        # set initial checked state from config
        self.update_checkbox_by_config_value()
        # update config on checkbox state
        self.stateChanged.connect(self.update_config_value_by_checkbox)
        # update checkbox on config change
        Config.config_change_callbacks.append(self.update_checkbox_by_config_value)

    def update_checkbox_by_config_value(self) -> None:
        varvalue = self.config.__dict__[self.varname]
        if (varvalue != self.isChecked()):
            self.setChecked(varvalue)

    def update_config_value_by_checkbox(self) -> None:
        self.config.__dict__[self.varname] = self.isChecked()
        Config.fire_config_changed_event()
        self.log.info(f"set {self.varname} to {self.config.__dict__[self.varname]}")