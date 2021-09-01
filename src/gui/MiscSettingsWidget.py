from PySide6.QtWidgets import QWidget, QGroupBox, QGridLayout, QComboBox, QFormLayout, QLabel, QVBoxLayout, QCheckBox
from qt_material import list_themes
from common.Config import Config
from common.LogHolder import LogHolder
from .ConfigVariableCheckBox import ConfigVariableCheckBox

class MiscSettingsWidget(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config

        group = QGroupBox("Misc.")
        stay_on_top_checkbox = ConfigVariableCheckBox(self.config, f"{self.config.is_stay_on_top=}", "Stay on top")
        theme_chooser = self.create_theme_chooser()

        # Flip image vertically
        flip_checkbox = QCheckBox()
        flip_checkbox.setText("Flip image")
        self.config.capture_flip.subscribe_and_run(lambda new_value: flip_checkbox.setChecked(new_value))
        flip_checkbox.stateChanged.connect(lambda new_value: self.config.capture_flip.set_value(new_value != 0))  # type: ignore

        # Layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(group)

        grid_layout = QGridLayout()
        group.setLayout(grid_layout)

        grid_layout.addWidget(flip_checkbox, 0, 0)
        grid_layout.addWidget(stay_on_top_checkbox, 1, 0)

        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Theme"), theme_chooser)
        grid_layout.addLayout(form_layout, 2, 0)

    def create_theme_chooser(self) -> QWidget:
        combo = QComboBox()
        themes = list_themes()
        for theme in themes:
            theme_name = str.title(theme.replace(".xml", "").replace("_", " "))
            combo.addItem(theme_name, userData=theme)

        self.config.ui_theme.subscribe_and_run(lambda new_theme_name: combo.setCurrentIndex(themes.index(new_theme_name)))
        combo.currentIndexChanged.connect(lambda new_theme_index: self.config.ui_theme.set_value(themes[new_theme_index]))

        return combo