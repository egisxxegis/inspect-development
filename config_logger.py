import logging

import platform_consts as Const


def config_logger():
    """Sets log level, format. Calling this method one time is the same as calling it many times.
    Would not work if logging was previously configured using other settings."""

    logging.basicConfig(format=Const.LOGGING_FORMAT, level=Const.LOGGING_LEVEL)
