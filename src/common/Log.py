import logging

def init_logging() -> None:
    log = logging.getLogger("initLoggingLogger")
    log.info("initializing logging")

    logging_format = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s - %(message)s'

    # create logger
    root_logger = logging.getLogger('root')
    root_logger.setLevel(logging.DEBUG)

    # remove other handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # add console handler
    console_handler = logging.StreamHandler()
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