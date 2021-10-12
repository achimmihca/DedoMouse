from __future__ import annotations

from typing import Callable

from rx.subject import Subject
from .util import get_time_ms
from .SignalFlankRecognizer import SignalFlankRecognizer

class SignalHoldRecognizer:
    no_value = 0
    high_value = 1
    high_hold_value = 2
    low_value = 3
    low_hold_value = 4

    def __init__(self, signal_flank_recognizer: SignalFlankRecognizer, hold_duration_threshold_ms_getter: Callable[[], int]) -> None:
        self.signal_flank_recognizer = signal_flank_recognizer
        self.hold_duration_threshold_ms_getter = hold_duration_threshold_ms_getter
        self.state = SignalHoldRecognizer.no_value
        self.last_rising_flank_time_ms = 0
        self.last_falling_flank_time_ms = 0
        self.hold_high_event_stream = Subject()
        self.hold_low_event_stream = Subject()

        self.signal_flank_recognizer.rising_flank_event_stream.subscribe(self.on_rising_flank)
        self.signal_flank_recognizer.falling_flank_event_stream.subscribe(self.on_falling_flank)

    def on_rising_flank(self, value: bool) -> None:
        if self.state is SignalHoldRecognizer.low_hold_value:
            self.hold_low_event_stream.on_next(False)
        self.state = SignalHoldRecognizer.high_value
        self.last_rising_flank_time_ms = get_time_ms()

    def on_falling_flank(self, value: bool) -> None:
        if self.state is SignalHoldRecognizer.high_hold_value:
            self.hold_high_event_stream.on_next(False)
        self.state = SignalHoldRecognizer.low_value
        self.last_falling_flank_time_ms = get_time_ms()

    def update(self, current_time_ms: int) -> None:
        if self.state is SignalHoldRecognizer.high_value:
            if self.last_rising_flank_time_ms + self.hold_duration_threshold_ms_getter() < current_time_ms:
                self.state = SignalHoldRecognizer.high_hold_value
                self.hold_high_event_stream.on_next(True)
        elif self.state is SignalHoldRecognizer.low_value:
            if self.last_falling_flank_time_ms + self.hold_duration_threshold_ms_getter() < current_time_ms:
                self.state = SignalHoldRecognizer.low_hold_value
                self.hold_low_event_stream.on_next(True)
