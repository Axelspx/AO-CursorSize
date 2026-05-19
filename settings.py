import winreg
import ctypes
import os
import sys

## CONSTANTS ##
USER32 = ctypes.WinDLL("user32", use_last_error=True)
USER32.SystemParametersInfoW.restype = ctypes.c_bool
USER32.SystemParametersInfoW.argtypes = [
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
SIZE_REG = "selected_size"
CURSOR_REG = "cursor_index"
CURSOR = ["Cursor_y.png", "Cursor_b.png", "Cursor.png"]

cursor_index: int= 0    # 0, 1, 2
selected_size: int= SIZE_DEFAULT
current_size: int= SIZE_DEFAULT
is_ao_focus: bool= False
debug: bool= False



## HELPERS ##
def debug_print(msg: str) -> None:
    # Print debug msgs when debug = True
    if debug:
        print(msg)

def cycle_cursor_icon() -> None:
    # Cycles cursor icon index 0-2, wraps back to 0 after index 2
    global cursor_index
    cursor_index = (cursor_index + 1) % len(CURSOR)
    debug_print(f"Cursor index cycled to: {cursor_index}")

def get_cursor_icon() -> str:
    return CURSOR[cursor_index]

def get_data_path(orig_path:str) -> str:
    # Post/pre pyinstaller freeze additional data(Icons) path
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, orig_path)
    return os.path.abspath(orig_path)

def get_exe_path() -> str|bool:
    # Return executable path if running via executable file
    if hasattr(sys, "frozen"):
        return sys.executable
    else:
        debug_print("Could not return path: not frozen/executable.")
        return False


## REGISTRY ##
def load_reg(name:str) -> int|bool:
    # Query then return registry key value
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\AO_Cursor_Size")
        value = winreg.QueryValueEx(key, name)[0]
        winreg.CloseKey(key)
        debug_print(f"Loaded reg [{name}: {value}] from registry.")
        return value
    except (FileNotFoundError, OSError):
        debug_print("ERROR: Unable to load selected size from registry.")
        return False

def save_reg(name:str, value:int) -> None:
    # Create/overwrite registry key value
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\AO_Cursor_Size")
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(key)
        debug_print(f"Saved registry [{name}: {value}] to registry.")
    except OSError:
        debug_print("ERROR: Unable to save selected size to registry.")


## Startup ##
def set_startup(value: bool) -> None:
    # Create / delete CurrentVersion and StartupApproved registry entry according to passed value
    if not hasattr(sys, "frozen"):
        debug_print("Could not set startup: not frozen/executable.")
        return
    try:
        key_current_ver = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        key_start_appr = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_READ,
            )
        if value: # True
            winreg.SetValueEx(key_current_ver, "AO_Cursor_Size", 0, winreg.REG_SZ, get_exe_path())
            # Set startup enabled by creating registry entry for AO Cursor Size.
            try:
                start_appr_value = winreg.QueryValueEx(key_start_appr, "AO_Cursor_Size")[0]
                if b'\03' in start_appr_value:
                    winreg.DeleteValue(key_start_appr, "AO_Cursor_Size")
            except FileNotFoundError:
                pass
        else: # False
            winreg.DeleteValue(key_current_ver, "AO_Cursor_Size")
        winreg.CloseKey(key_current_ver)
        winreg.CloseKey(key_start_appr)
        debug_print(f"Set startup {value}")
    except FileNotFoundError:
        debug_print(r"Could not set startup: AO_Cursor_Size reg key in 'CurrentVersion\Run' not found")
    except OSError:
        debug_print("ERROR: No change was made to registry")

def is_startup() -> bool:
    # Query AO_Cursor_Size startup registry value and task manager startup registry value, return according to existence
    # and according to if StartupApproved allows startup to run
    if not hasattr(sys, "frozen"):
        return False
    try:
        key_current_ver = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run"
        )
        key_start_appr = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
            0,
            winreg.KEY_READ,
        )
        value1 = winreg.QueryValueEx(key_current_ver, "AO_Cursor_Size")[0]
        try:
            start_appr_value = winreg.QueryValueEx(key_start_appr, "AO_Cursor_Size")[0]
            if b'\x03' in start_appr_value:
                value2 = False
                debug_print(r"Startup cannot run: x03 entry in 'StartupApproved\Run'")
            else:
                value2 = True
                debug_print(r"Startup can run: non x03 entry in 'StartupApproved\Run'")
        except FileNotFoundError:
            debug_print(r"Startup can run: no entry in 'StartupApproved\Run'")
            value2 = True
        winreg.CloseKey(key_current_ver)
        winreg.CloseKey(key_start_appr)
        result = value1==get_exe_path() and value2
        print(f"Startup: {result}")
        return result
    except FileNotFoundError:
        debug_print(r"Startup disabled: AO_Cursor_Size does not exist in 'CurrentVersion\Run'")
        return False
    except OSError:
        return False







