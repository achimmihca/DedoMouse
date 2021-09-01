from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from common.LogHolder import LogHolder

class RequireAppRestartLabel(QLabel, LogHolder):
    def __init__(self) -> None:
        QLabel.__init__(self)
        LogHolder.__init__(self)

        self.setText("Requires restart")
        self.setToolTip("These parameters require a restart of the app.")
        self.setAlignment(Qt.AlignCenter)
        self.setProperty("cssClass", "highlight") # type: ignore