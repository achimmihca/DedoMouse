from __future__ import annotations
from typing import Any, Optional, TypeVar, Union
from rx.core import typing
from rx.core.typing import Observable
from rx.subject.subject import Subject

T = TypeVar('T')

class ReactiveProperty(Observable[T]):
    def __init__(self, initialValue: T = None) -> None:
        super().__init__()
        self.subject = Subject()
        self.subject.pipe()
        self.value = initialValue
    
    def subscribe(self, # pylint: disable=arguments-differ
            observer: Optional[Union[typing.Observer, typing.OnNext]] = None,
            on_error: Optional[typing.OnError] = None,
            on_completed: Optional[typing.OnCompleted] = None,
            on_next: Optional[typing.OnNext] = None,
            *,
            scheduler: Optional[typing.Scheduler] = None,
            ) -> typing.Disposable:
        return self.subject.subscribe(observer=observer, on_error=on_error, on_completed=on_completed, on_next=on_next, scheduler=scheduler)

    def subscribeAndRun(self, # pylint: disable=arguments-differ
            observer: Optional[Union[typing.Observer, typing.OnNext]] = None,
            on_error: Optional[typing.OnError] = None,
            on_completed: Optional[typing.OnCompleted] = None,
            on_next: Optional[typing.OnNext] = None,
            *,
            scheduler: Optional[typing.Scheduler] = None,
            ) -> typing.Disposable:
        res = self.subscribe(observer=observer, on_error=on_error, on_completed=on_completed, on_next=on_next, scheduler=scheduler)
        if self.value:
            if on_next:
                on_next(self.value)
            elif observer and callable(observer):
                observer(self.value)
        return res

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if (name == "value" and self.value):
            self.subject.on_next(value)
