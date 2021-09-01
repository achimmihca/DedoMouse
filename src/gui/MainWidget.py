from typing import Callable
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QTabWidget, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLayout, QScrollArea, QSizePolicy, QGroupBox
from common.Config import Config
from common.LogHolder import LogHolder
from .SettingsWidget import SettingsWidget
from .ToggleButton import ToggleButton
from .ConfigVariableToggleButton import ConfigVariableToggleButton

class MainWidget(QWidget, LogHolder):
    def __init__(self, config: Config, close_callback: Callable) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.close_callback = close_callback

        # Label for video image
        self.image_label = QLabel("Starting Camera...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(QSize(int(160), int(120)))

        # Settings in vertical scroll area
        settings_widget = SettingsWidget(self.config)

        # Buttons to toggle mouse control and show/hide settings
        button_layout = self.create_button_layout(settings_widget)

        # Layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.image_label, 1)
        v_layout.addLayout(button_layout)

        main_layout.addLayout(v_layout, 3)
        main_layout.addWidget(settings_widget, 2)

    def create_button_layout(self, settings_widget: QWidget) -> QLayout:
        control_position_toggle = ConfigVariableToggleButton(self.config,
                                                             f"{self.config.is_control_mouse_position=}",
                                                             "images/svg/control-position.svg",
                                                             "Control mouse position",
                                                             self.config.toggle_control_mouse_position_shortcuts.value)
        control_click_toggle = ConfigVariableToggleButton(self.config,
                                                          f"{self.config.is_control_click=}",
                                                          "images/svg/control-click.svg",
                                                          "Control click",
                                                          self.config.toggle_control_click_shortcuts.value)
        control_scroll_toggle = ConfigVariableToggleButton(self.config,
                                                           f"{self.config.is_control_scroll=}",
                                                           "images/svg/control-scroll.svg",
                                                           "Control scroll",
                                                           self.config.toggle_control_scroll_shortcuts.value)
        control_disable_all_toggle = ConfigVariableToggleButton(self.config,
                                                                f"{self.config.is_all_control_disabled=}",
                                                                "images/svg/disable-all.svg",
                                                                "Disable all mouse controls",
                                                                self.config.toggle_all_control_disabled_shortcuts.value)

        settings_button = ToggleButton("images/svg/settings.svg", "Show/hide settings")
        settings_button.setChecked(self.config.is_show_settings.value)
        settings_button.clicked.connect(lambda: self.config.is_show_settings.set_value(settings_button.isChecked())) # type: ignore
        self.config.is_show_settings.subscribe_and_run(lambda new_value: settings_widget.setVisible(new_value))

        layout = QHBoxLayout()
        layout.addWidget(control_position_toggle)
        layout.addWidget(control_click_toggle)
        layout.addWidget(control_scroll_toggle)
        layout.addWidget(control_disable_all_toggle)
        layout.addWidget(QLabel(), 1)
        layout.addWidget(settings_button)

        return layout