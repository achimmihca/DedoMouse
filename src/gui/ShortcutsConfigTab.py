from typing import List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QFormLayout, QGroupBox, QLineEdit, QLabel
from common.Config import Config
from common.ReactiveProperty import ReactiveProperty
from common.LogHolder import LogHolder
from .qt_util import new_label

class ShortcutsConfigTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)

        form_layout.addRow(new_label("Toggle Position", None), self.create_shortcut_control(self.config.toggle_control_mouse_position_shortcuts))
        form_layout.addRow(new_label("Toggle Click", None), self.create_shortcut_control(self.config.toggle_control_click_shortcuts))
        form_layout.addRow(new_label("Toggle Scroll", None), self.create_shortcut_control(self.config.toggle_control_scroll_shortcuts))
        form_layout.addRow(new_label("Toggle Disable All", None), self.create_shortcut_control(self.config.toggle_all_control_disabled_shortcuts))

        # Warning label
        label = QLabel("Parameters of this tab require a restart")
        label.setAlignment(Qt.AlignCenter)
        label.setProperty("cssClass", "highlight")  # type: ignore
        self.layout().addWidget(label)

    def create_shortcut_control(self, reactive_property: ReactiveProperty[List[str]]) -> QLineEdit:
        text_edit = QLineEdit()

        def on_text_changed() -> None:
            shortcuts = [shortcut.strip(" ") for shortcut in text_edit.text().split(",") if len(shortcut.strip(" ")) > 0]
            reactive_property.value = shortcuts

        reactive_property.subscribe_and_run(lambda new_values: text_edit.setText(", ".join(new_values)))
        text_edit.textChanged.connect(on_text_changed) # type: ignore

        return text_edit