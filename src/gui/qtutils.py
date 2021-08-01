from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

def newGroup(title:str, widget: QWidget) -> QGroupBox:
    layout = QVBoxLayout()
    layout.addWidget(widget)
    group = QGroupBox(title)
    group.setLayout(layout)
    return group

def newLabel(text: str, tooltip: str) -> QLabel:
    label = QLabel(text)
    label.setToolTip(tooltip)
    return label