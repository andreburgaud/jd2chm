"""
Exposes methods to change the color of the output in a console.
"""
from ctypes import *

BRIGHT=True

# winbase.h
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

# wincon.h
FOREGROUND_BLACK = 0x0000
FOREGROUND_BLUE = 0x0001
FOREGROUND_GREEN = 0x0002
FOREGROUND_CYAN = 0x0003
FOREGROUND_RED = 0x0004
FOREGROUND_MAGENTA = 0x0005
FOREGROUND_YELLOW = 0x0006
FOREGROUND_GREY = 0x0007
DEFAULT_COLOR = FOREGROUND_GREY

FOREGROUND_INTENSITY = 0x0008  # foreground color is intensified.

BACKGROUND_BLACK = 0x0000
BACKGROUND_BLUE = 0x0010
BACKGROUND_GREEN = 0x0020
BACKGROUND_CYAN = 0x0030
BACKGROUND_RED = 0x0040
BACKGROUND_MAGENTA = 0x0050
BACKGROUND_YELLOW = 0x0060
BACKGROUND_GREY = 0x0070

BACKGROUND_INTENSITY = 0x0080  # background color is intensified.

h_stdout = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute


def set_color(color=0):
    if color:
        SetConsoleTextAttribute(h_stdout, color)
    else:
        SetConsoleTextAttribute(h_stdout, DEFAULT_COLOR)


def set_bright_color(color=0):
    if color:
        SetConsoleTextAttribute(h_stdout, color | FOREGROUND_INTENSITY)
    else:
        SetConsoleTextAttribute(h_stdout, DEFAULT_COLOR | FOREGROUND_INTENSITY)


def style(color=0, bright=False):
    """Returns function that returns decorator. This allows to mimic a decorator that takes parameters
    Wrapped function may take parameters or no paramters"""
    def decor_set_color(func):
        def wrapper(args=None):
            if bright:
                SetConsoleTextAttribute(h_stdout, color | FOREGROUND_INTENSITY)
            else:
                SetConsoleTextAttribute(h_stdout, color)
            if args:
                func(args)
            else:
                func()
            if bright:
                SetConsoleTextAttribute(h_stdout, DEFAULT_COLOR | FOREGROUND_INTENSITY)
            else:
                SetConsoleTextAttribute(h_stdout, DEFAULT_COLOR)
        return wrapper
    return decor_set_color


@style(color=FOREGROUND_RED, bright=True)
def print_error(msg):
    """Print error with coloring based on the style."""
    print(msg)
