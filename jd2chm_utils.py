import os
import sys
import shutil

import jd2chm_log as log
import jd2chm_conf as conf
import jd2chm_const as const

logging = None
config = None


def get_app_dir():
    if hasattr(sys, "frozen"):  # py2exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])


def get_logging(level=2):
    global logging
    if not logging:
        logging = log.Jd2chmLogging(level)
    return logging


def get_log():
    """Facilitate sharing the logger across the different modules."""
    return get_logging().logger


def get_conf():
    global config
    if not config:
        config = conf.Jd2chmConfig()
        config.init()
    return config


def term_width():
    return shutil.get_terminal_size((const.DEFAULT_TERM_WIDTH,
                                     const.DEFAULT_TERM_HEIGHT)).columns - const.TERM_MARGIN


def center(line, max_line=0):
    """Center a padded string based on the width of the terminal.

    If max_line is provided for justified text, line shorter than max_line
    will only be padded on the left side.
    """

    width = term_width()
    left_margin = (width - max_line) / 2
    if len(line) < max_line:
        return (' ' * int(left_margin)) + line
    return line.center(width, ' ')


def print_center_block(text, max_line=0):
    """Print a block of text centered on the terminal."""

    for line in text.split('\n'):
        print(center(line, max_line))
