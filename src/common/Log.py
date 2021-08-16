import logging
import sys

logging_format = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s - %(message)s'

def init_logging() -> None:
    global logging_format

    log = logging.getLogger("initLoggingLogger")
    log.info("initializing logging")

    # create logger
    root_logger = logging.getLogger('root')
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

    logging.StreamHandler()
    
    log.info("init logging done")