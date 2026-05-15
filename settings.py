import winreg
import ctypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SystemParametersInfoW.restype = ctypes.c_bool
user32.SystemParametersInfoW.argtypes = [
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_void_p,
    ctypes.c_uint,
]

SPI_SETCURSORSIZE = 0x2029
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

IGNORED_TITLES = [None, "", "Task Switching"]
AO_TITLE = "Albion Online Client"
SIZE_DEFAULT = 32 # Windows default (Accessibility cursor size slider value 1)

selected_size = SIZE_DEFAULT
current_size = SIZE_DEFAULT
is_ao_focus = False


