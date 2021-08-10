from typing import Callable
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QTabWidget, QWidget, QLabel, QPushButton, QVBoxLayout
from common.Config import Config
from common.LogHolder import LogHolder
from .MonitorConfigTab import MonitorConfigTab
from .OtherConfigTab import OtherConfigTab
from .VideoConfigTab import VideoConfigTab
from .EnabledMouseActionsTab import EnabledMouseActionsTab

class MainWidget(QWidget, LogHolder):
    def __init__(self, config: Config, close_callback: Callable) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.close_callback = close_callback

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Label for video image
        self.image_label = QLabel("Starting Camera...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(QSize(int(160), int(120)))
        self.main_layout.addWidget(self.image_label, 1)

        # Quit button
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_callback)
        self.main_layout.addWidget(self.quit_button)

        # Tabs for configuration
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.tab_widget.addTab(EnabledMouseActionsTab(config), "Controls")
        self.tab_widget.addTab(MonitorConfigTab(config), "Monitor")
        self.tab_widget.addTab(VideoConfigTab(config), "Video")
        self.tab_widget.addTab(OtherConfigTab(config), "Misc.")
