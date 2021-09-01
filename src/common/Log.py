from typing import Any
import logging
import sys

logging_format = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s - %(message)s'

def init_logging() -> None:
    log = logging.getLogger("initLoggingLogger")
    log.info("initializing logging")

    # register uncaught exception callback
    sys.excepthook = handle_uncaught_exception

    # create logger
    root_logger = logging.getLogger("root")
    root_logger.setLevel(logging.DEBUG)

    # remove other handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(logging_format)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # add file handler
    console_handler = logging.FileHandler(filename="dedo_mouse.log", mode="w", encoding="utf-8")
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(logging_format)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    log.info("init logging done")


def handle_uncaught_exception(exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.getLogger("root").error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))