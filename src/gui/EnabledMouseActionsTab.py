from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, QComboBox, QFormLayout, QLabel
from qt_material import list_themes
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
        grid_layout = QGridLayout()
        group.setLayout(grid_layout)

        grid_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_mouse_position=}", "Position"), 0, 0)
        grid_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_click=}", "Click"), 0, 1)
        grid_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_control_scroll=}", "Scroll"), 0, 2)
        grid_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_all_control_disabled=}", "Disable all"), 1, 0)

        return group

    def create_other_controls(self) -> QWidget:
        group = QGroupBox("Misc.")
        grid_layout = QGridLayout()
        group.setLayout(grid_layout)

        grid_layout.addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_stay_on_top=}", "Stay on top"), 0, 0)

        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Theme"), self.create_theme_chooser())

        grid_layout.addLayout(form_layout, 1, 0)

        return group

    def create_theme_chooser(self) -> QWidget:
        combo = QComboBox()
        themes = list_themes()
        for theme in themes:
            theme_name = str.title(theme.replace(".xml", "").replace("_", " "))
            combo.addItem(theme_name, userData=theme)

        self.config.ui_theme.subscribe_and_run(lambda new_theme_name: combo.setCurrentIndex(themes.index(new_theme_name)))
        combo.currentIndexChanged.connect(lambda new_theme_index: self.config.ui_theme.set_value(themes[new_theme_index]))

        return combo