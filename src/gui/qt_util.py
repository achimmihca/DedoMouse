from typing import Union
from PySide6.QtWidgets import QLabel

def new_label(text: str, tooltip: Union[str, None]) -> QLabel:
    label = QLabel(text)
    if tooltip is not None:
        label.setToolTip(tooltip)
    return label