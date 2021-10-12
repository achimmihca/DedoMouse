from __future__ import annotations
from rx.subject import Subject

class SignalFlankRecognizer:
    def __init__(self, initial_value: bool) -> None:
        self.value = initial_value
        self.rising_flank_event_stream = Subject()
        self.falling_flank_event_stream = Subject()
        self.any_flank_event_stream = Subject()

    def set_value(self, new_value: bool) -> None:
        if self.value and not new_value:
            self.falling_flank_event_stream.on_next(True)
            self.any_flank_event_stream.on_next(False)
        elif not self.value and new_value:
            self.rising_flank_event_stream.on_next(True)
            self.any_flank_event_stream.on_next(True)
        self.value = new_value
