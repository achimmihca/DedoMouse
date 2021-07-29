import logging

class LogHolder:
    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)