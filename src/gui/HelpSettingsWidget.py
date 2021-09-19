from typing import List
from PySide6.QtWidgets import QWidget, QGroupBox, QLabel, QVBoxLayout, QGridLayout
from common.Config import Config
from common.LogHolder import LogHolder

class HelpSettingsWidget(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        self.label_row_count = 0

        group = QGroupBox("Help")
        grid_layout = QGridLayout()
        group.setLayout(grid_layout)

        self.add_label_row(grid_layout, ["Left Click", "Move index finger near thumb."])
        self.add_label_row(grid_layout, ["Right Click", "Move middle and ring finger near thumb."])
        self.add_label_row(grid_layout, ["Middle Click", "Move ring finger and pinky near thumb."])
        self.add_label_row(grid_layout, ["Scroll Up/Down", "Make thumb up/down gesture."])

        # Layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(group)

        main_layout.addWidget(group)

    def add_label_row(self, grid_layout: QGridLayout, texts: List[str]) -> None:
        row_span = 1
        column = 0
        for text in texts:
            column_span = 1 if column == 0 else 3
            label = QLabel(text)
            if column == 0:
                label.setProperty("cssClass", "title_column") # type: ignore
            grid_layout.addWidget(label, self.label_row_count, column, row_span, column_span)
            column = column + 1
        self.label_row_count = self.label_row_count + 1