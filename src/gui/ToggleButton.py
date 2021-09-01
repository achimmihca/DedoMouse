from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton, QSizePolicy
from typing import Any, List
from common.Config import Config
from common.LogHolder import LogHolder

class ToggleButton(QToolButton, LogHolder):
    def __init__(self, image_path: str, tooltip: str, shortcuts: List[str]=None) -> None:
        QToolButton.__init__(self)
        LogHolder.__init__(self)
        self.setIcon(QIcon(image_path))
        self.setIconSize(QSize(64, 64))
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setCheckable(True)

        shortcuts_csv = ", ".join(shortcuts) if shortcuts else None
        tooltip_with_shortcuts = tooltip if not shortcuts_csv else (tooltip + f" ({shortcuts_csv})")
        self.setToolTip(tooltip_with_shortcuts)
