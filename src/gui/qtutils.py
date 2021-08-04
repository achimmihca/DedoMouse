from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

def new_group(title: str, widget: QWidget) -> QGroupBox:
    layout = QVBoxLayout()
    layout.addWidget(widget)
    group = QGroupBox(title)
    group.setLayout(layout)
    return group

def new_label(text: str, tooltip: str) -> QLabel:
    label = QLabel(text)
    label.setToolTip(tooltip)
    return label