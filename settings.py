import winreg
import ctypes
import os
import sys

## CONSTANTS ##
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
TITLE = "AO Cursor Size"
SIZE_DEFAULT = 32 # Windows default (Accessibility cursor size slider value 1)

## GLOBALS ##
selected_size: int= SIZE_DEFAULT
current_size: int= SIZE_DEFAULT
is_ao_focus: bool= False


## REGISTRY ##
def load_selected_size() -> None:
    global selected_size
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\AO_Cursor_Size")
        selected_size = winreg.QueryValueEx(key, "selected_size")[0]
        winreg.CloseKey(key)
        print(f"Loaded saved selected size({selected_size}) from registry.")
    except (FileNotFoundError, OSError):
        selected_size = SIZE_DEFAULT
        print("ERROR: Unable to load selected size from registry.")

def save_selected_size() -> None:
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\AO_Cursor_Size")
        winreg.SetValueEx(key, "selected_size", 0, winreg.REG_DWORD, selected_size)
        winreg.CloseKey(key)
        print(f"Saved selected size({selected_size}) to registry.")
    except OSError:
        print("ERROR: Unable to save selected size to registry.")

def set_startup(value: bool) -> None:
    if not hasattr(sys, "frozen"):
        print("Could not set startup: not frozen/executable.")
        return
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
            )
        if value:
            winreg.SetValueEx(key, "AO_Cursor_Size", 0, winreg.REG_SZ, get_exe_path())
        else:
            winreg.DeleteValue(key, "AO_Cursor_Size")
        winreg.CloseKey(key)
    except FileNotFoundError:
        print(f"Could not set startup {value}: reg value not found.")
    except OSError:
        print("ERROR: No change was made to registry.")

def is_startup() -> bool:
    if not hasattr(sys, "frozen"):
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
        startup_value = winreg.QueryValueEx(key, "AO_Cursor_Size")[0]
        winreg.CloseKey(key)
        return startup_value == get_exe_path()

    except FileNotFoundError:
        print("Could not check startup: AO_Cursor_Size reg value not found.")
        return False
    except OSError:
        return False

def get_data_path(orig_path:str) -> str:
    if hasattr(sys, "_MEIPASS"):
        # Pyinstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, orig_path)
    return os.path.abspath(orig_path)

def get_exe_path() -> str|bool:
    if hasattr(sys, "frozen"):
        # Compiled
        return sys.executable
    else:
        # Running from terminal
        print("Could not return path: not frozen/executable.")
        return False





