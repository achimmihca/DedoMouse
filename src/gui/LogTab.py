import logging
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox, QSpinBox, QGroupBox, QPlainTextEdit
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QTextCursor
from common.Config import Config
from common.LogHolder import LogHolder
from common.Log import logging_format
from common.Vector import Vector
from screeninfo import get_monitors
from .qt_util import new_label

class LogTab(QWidget, LogHolder):
    def __init__(self, config: Config) -> None:
        global logging_format

        QWidget.__init__(self)
        LogHolder.__init__(self)
        self.config = config

        text_edit_logger = QTextEditLogger(self)
        text_edit_logger.setFormatter(logging.Formatter(logging_format))
        logging.getLogger().addHandler(text_edit_logger)
        logging.getLogger().setLevel(logging.INFO)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(text_edit_logger.text_edit)

class LogSignalHolder(QObject):
    sig = Signal(str)

    def __init__(self) -> None:
        QObject.__init__(self)

    def do_emit(self) -> None:
        self.sig.emit("") # type: ignore

    def do_connect(self, callback: Any) -> None:
        self.sig.connect(callback) # type: ignore

class QTextEditLogger(logging.Handler):
    def __init__(self, parent: QWidget) -> None:
        super().__init__()
        self.text_edit = QPlainTextEdit(parent)
        self.text_edit.setReadOnly(True)
        self.text_edit.setCenterOnScroll(True)

        self.log_messages = ""
        self.max_length = 10000

        self.log_signal_holder = LogSignalHolder()
        self.log_signal_holder.do_connect(self.update_text_edit_text)

    def update_text_edit_text(self) -> None:
        self.text_edit.setPlainText(self.log_messages)

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)

        self.text_edit.ensureCursorVisible()

    # emit method of logging.Handler is called for every log message
    def emit(self, record: Any) -> None:
        msg = self.format(record)
        self.log_messages += msg
        self.log_messages += "\n"
        # Only show the last N characters of the log
        if (len(self.log_messages) > self.max_length):
            self.log_messages = self.log_messages[-self.max_length:]

        # Trigger signal to handle the new log message on the main thread
        self.log_signal_holder.do_emit()