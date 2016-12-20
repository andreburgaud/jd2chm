"""
Logging class for jd2chm
"""

import logging
import lib_console as console


class WinHandler(logging.Handler):
    """EditCtrl Handler"""

    def __init__(self, win):
        logging.Handler.__init__(self)
        self.win = win

    def emit(self, record):
        if self.win:
            line = self.format(record)
            self.win.addLogText(line)


class ColorHandler(logging.StreamHandler):
    """Color handler for the console"""

    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        if record.levelno == logging.DEBUG:
            console.set_color(console.FOREGROUND_GREEN)
        if record.levelno == logging.WARNING:
            console.set_color(console.FOREGROUND_YELLOW)
        if record.levelno == logging.ERROR:
            console.set_color(console.FOREGROUND_RED)
        if record.levelno == logging.CRITICAL:
            console.set_bright_color(console.FOREGROUND_RED)
        line = self.format(record)
        print(line)
        console.set_color()


class Jd2chmLogging:
    def __init__(self, level=2):
        self.logger = logging.getLogger('jd2chm')
        # self.formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(message)s')
        self.formatter = logging.Formatter('[%(asctime)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        self.setLevel(level)
        # self.stream_handler = logging.StreamHandler()
        self.stream_handler = ColorHandler()
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

    def addWinHandler(self, win):
        """Add a windows handler to allow logging in the GUI."""
        self.win_handler = WinHandler(win)
        self.win_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.win_handler)

    def setLogFile(self, log_file):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def setLevel(self, level=2):
        """level is between 0 and 5. In the module logging, we have: CRITICAL = 50,
        ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10, NOTSET = 0.
        """
        if level not in range(6):
            level = 2
        self.logger.setLevel(level * 10)

    def shutdown(self):
        logging.shutdown()
