import logging

def initLogging() -> None:
    logging_format = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s - %(message)s'

    # create logger
    rootLogger = logging.getLogger('root')
    rootLogger.setLevel(logging.DEBUG)

    # add console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(logging_format)
    consoleHandler.setFormatter(formatter)
    rootLogger.addHandler(consoleHandler)

    # add file handler
    consoleHandler = logging.FileHandler(filename="dedo_mouse.log", mode="w", encoding="utf-8")
    consoleHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(logging_format)
    consoleHandler.setFormatter(formatter)
    rootLogger.addHandler(consoleHandler)
    