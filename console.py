"""
Exposes methods to change the color of the output in a console (Windows specific).
"""
import collections
from ctypes import windll, Structure, c_short, c_ushort, byref

SHORT = c_short
WORD = c_ushort


class COORD(Structure):
    """struct in wincon.h."""
    _fields_ = [
        ("X", SHORT),
        ("Y", SHORT)]


class SMALL_RECT(Structure):
    """struct in wincon.h."""
    _fields_ = [
        ("Left", SHORT),
        ("Top", SHORT),
        ("Right", SHORT),
        ("Bottom", SHORT)]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    """struct in wincon.h."""
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", WORD),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD)]

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


DefaultColors = collections.namedtuple('DefaultColors', ['colors', 'foreground', 'background'])
BRIGHT = True
default_colors = None

h_stdout = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo


def default():
    """Retrieve default console attributes (colors)"""
    global default_colors
    if not default_colors:
        # Built only once
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        default_colors = GetConsoleScreenBufferInfo
        GetConsoleScreenBufferInfo(h_stdout, byref(csbi))
        default_colors = DefaultColors(colors=csbi.wAttributes,
                                       foreground=csbi.wAttributes & 0x0007,
                                       background=csbi.wAttributes & 0x0070)
    return default_colors


def get_text_attr():
    """Returns the character attributes (colors) of the console screen buffer."""
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    GetConsoleScreenBufferInfo(h_stdout, byref(csbi))
    return DefaultColors(colors=csbi.wAttributes, background=csbi.wAttributes & 0x0070)


def set_color(color=0):
    """Set a color (non bright)"""
    if color:
        SetConsoleTextAttribute(h_stdout, color | default().background )
    else:
        SetConsoleTextAttribute(h_stdout, default().colors)


def set_bright_color(color=0):
    """Set a bright color for the console."""
    if color:
        SetConsoleTextAttribute(h_stdout, color | default().background | FOREGROUND_INTENSITY)
    else:
        SetConsoleTextAttribute(h_stdout, default().colors | FOREGROUND_INTENSITY)


def style(color=0, bright=False):
    """Returns function that returns decorator. This allows to mimic a decorator that takes parameters
    Wrapped function may take parameters or no parameters"""
    def decor_set_color(func):
        def wrapper(args=None):
            if bright:
                SetConsoleTextAttribute(h_stdout, color | default().background | FOREGROUND_INTENSITY)
            else:
                SetConsoleTextAttribute(h_stdout, color | default().background)
            if args:
                func(args)
            else:
                func()
            SetConsoleTextAttribute(h_stdout, default().colors)
        return wrapper
    return decor_set_color


@style(color=FOREGROUND_RED, bright=True)
def print_error(msg):
    """Print error with coloring based on the style."""
    print(msg)
