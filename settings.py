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
SIZE_DEFAULT = 32 # Windows default (Accessibility cursor size slider value 1)

## GLOBALS ##
selected_size: int= SIZE_DEFAULT
current_size: int= SIZE_DEFAULT
is_ao_focus: bool= False


## REGISTRY ##
def load_selected_size() -> None:
    global selected_size
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\AO_Cursor")
        selected_size = winreg.QueryValueEx(key, "selected_size")[0]
        winreg.CloseKey(key)
        print(f"Loaded saved selected size({selected_size}) from registry.")
    except (FileNotFoundError, OSError):
        selected_size = SIZE_DEFAULT
        print("ERROR: Unable to load selected size from registry.")

def save_selected_size() -> None:
    try:
        key =  winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\AO_Cursor")
        winreg.SetValueEx(key, "selected_size", 0, winreg.REG_DWORD, selected_size)
        winreg.CloseKey(key)
        print(f"Saved selected size({selected_size}) to registry.")
    except OSError:
        print("ERROR: Unable to save selected size to registry.")

def set_startup():
    #TODO
    pass


## .EXE ##
def get_path(orig_path:str):
    if hasattr(sys, "_MEIPASS"):
        # Pyinstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, orig_path)
    return os.path.join(os.path.abspath("."), orig_path)




