from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QSlider
from common.Config import Config
from common.LogHolder import LogHolder
from .qt_util import new_label

class TimingSettingsWidget(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        group = QGroupBox("Timing")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        form_layout = QFormLayout()
        group_layout.addLayout(form_layout)

        main_layout.addWidget(group)

        self.click_delay_label_template = "Click delay ({value}s)"
        self.double_click_max_pause_label_template = "Double click interval ({value}s)"
        self.drag_delay_label_template = "Drag delay ({value}s)"

        # Widgets
        click_delay_slider = self.create_click_delay_slider()
        click_delay_label = new_label(self.click_delay_label_template, "Time to hold click gesture to trigger a mouse click")
        self.config.click_delay_ms.subscribe_and_run(lambda value: click_delay_label.setText(self.click_delay_label_template.replace("{value}", f"{(value/1000.0):.2f}")))

        double_click_max_pause_slider = self.create_double_click_max_pause_slider()
        double_click_max_pause_label = new_label(self.double_click_max_pause_label_template, "Maximum time between two click gestures to trigger a mouse double click")
        self.config.double_click_max_pause_ms.subscribe_and_run(lambda value: double_click_max_pause_label.setText(self.double_click_max_pause_label_template.replace("{value}", f"{(value/1000.0):.2f}")))

        drag_delay_slider = self.create_drag_delay_slider()
        drag_delay_label = new_label(self.drag_delay_label_template, "Time to hold click gesture to trigger a mouse drag.\n"
                                                                     "This time begins after a left click has been triggered.")
        self.config.drag_start_click_delay_ms.subscribe_and_run(lambda value: drag_delay_label.setText(self.drag_delay_label_template.replace("{value}", f"{(value/1000.0):.2f}")))

        # Layout
        form_layout.addRow(click_delay_label, click_delay_slider)
        form_layout.addRow(double_click_max_pause_label, double_click_max_pause_slider)
        form_layout.addRow(drag_delay_label, drag_delay_slider)

    def create_click_delay_slider(self) -> QWidget:
        slider = self.create_milliseconds_slider(0, 1000)

        self.config.click_delay_ms.subscribe_and_run(lambda value: slider.setValue(value))
        slider.valueChanged.connect(lambda new_value: self.config.click_delay_ms.set_value(new_value))

        return slider

    def create_drag_delay_slider(self) -> QWidget:
        slider = self.create_milliseconds_slider(500, 2000)

        self.config.drag_start_click_delay_ms.subscribe_and_run(lambda value: slider.setValue(value))
        slider.valueChanged.connect(lambda new_value: self.config.drag_start_click_delay_ms.set_value(new_value))

        return slider

    def create_double_click_max_pause_slider(self) -> QWidget:
        slider = self.create_milliseconds_slider(300, 1000)
        self.config.double_click_max_pause_ms.subscribe_and_run(lambda value: slider.setValue(value))
        slider.valueChanged.connect(lambda new_value: self.config.double_click_max_pause_ms.set_value(new_value))

        return slider

    def create_milliseconds_slider(self, min: int, max: int) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setSingleStep(25)
        slider.setPageStep(25)
        return slider
