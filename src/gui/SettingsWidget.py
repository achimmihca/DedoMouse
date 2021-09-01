from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QScrollArea, QSizePolicy, QGroupBox, QLabel
from common.LogHolder import LogHolder
from common.Config import Config
from .MiscSettingsWidget import MiscSettingsWidget
from .MonitorSettingsWidget import MonitorSettingsWidget
from .VideoSettingsWidget import VideoSettingsWidget
from .ShortcutsSettingsWidget import ShortcutsSettingsWidget
from .GeometrySettingsWidget import GeometrySettingsWidget

class SettingsWidget(QScrollArea, LogHolder):
    def __init__(self, config: Config) -> None:
        QScrollArea.__init__(self)
        LogHolder.__init__(self)
        self.config = config

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setWidget(self.create_content_widget())

    def create_content_widget(self) -> QWidget:
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)

        content_layout.addWidget(MiscSettingsWidget(self.config))
        content_layout.addWidget(MonitorSettingsWidget(self.config))
        content_layout.addWidget(GeometrySettingsWidget(self.config))
        content_layout.addWidget(VideoSettingsWidget(self.config))
        content_layout.addWidget(ShortcutsSettingsWidget(self.config))

        return content_widget