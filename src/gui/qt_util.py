from PySide6.QtWidgets import QLabel

def new_label(text: str, tooltip: str) -> QLabel:
    label = QLabel(text)
    label.setToolTip(tooltip)
    return label