from typing import Callable
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QTabWidget, QWidget, QLabel, QPushButton, QVBoxLayout

from Config import Config
from LogHolder import LogHolder
from gui.ConfigVariableCheckBox import ConfigVariableCheckBox
from gui.EnabledMouseActionsControl import EnabledMouseActionsControl
from gui.MonitorConfigControl import MonitorConfigControl
from gui.qtutils import new_group

class MainWidget(QWidget, LogHolder):
    def __init__(self, config: Config, close_callback: Callable) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.close_callback = close_callback

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.image_label = QLabel("Starting Camera...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(QSize(int(320), int(240)))
        self.main_layout.addWidget(self.image_label)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_callback)
        self.main_layout.addWidget(self.quit_button)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.first_tab = QWidget()
        self.tab_widget.addTab(self.first_tab, "Controls")
        self.first_tab.setLayout(QVBoxLayout())

        self.first_tab.layout().addWidget(new_group("Mouse Control", EnabledMouseActionsControl(self.config)))

        self.second_tab = QWidget()
        self.tab_widget.addTab(self.second_tab, "Config")
        self.second_tab.setLayout(QVBoxLayout())
        self.second_tab.layout().addWidget(new_group("Monitor Setup", MonitorConfigControl(self.config)))

        self.second_tab.layout().addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_trigger_additional_click_on_double_click=}", "Trigger additional click on double-click"))
        self.second_tab.layout().addWidget(ConfigVariableCheckBox(self.config, f"{self.config.is_stay_on_top=}", "Stay on top"))