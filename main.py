import win32gui
import keyboard
import os
from win32_window_monitor import *
import ctypes
from tray import Tray


SPI_SETCURSORSIZE = 0x2029
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SystemParametersInfoW.restype = ctypes.c_bool
user32.SystemParametersInfoW.argtypes = [
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_void_p,
    ctypes.c_uint,
    ]

IGNORED_TITLES = [None, "", "Task Switching"]
AO_TITLE = "Albion Online Client"
SIZE_DEFAULT = 32 # Windows default (Accessibility cursor size slider value 1)
SIZE_CUSTOM = 44

last_size = None
is_ao_focus = False



def set_cursor_size(size=SIZE_DEFAULT) -> bool:
    global last_size
    if last_size == size:
        return True
    print('Setting cursor size..')

    ok = user32.SystemParametersInfoW(
        SPI_SETCURSORSIZE,
        0,
        ctypes.c_void_p(size),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
        )

    if not ok:
        err = ctypes.get_last_error()
        print(f"SystemParametersInfoW failed, GetLastError={err}")
        return False
    print(f'Set cursor size to {size}')
    last_size = size
    return True


def on_event( # window change foreground events
        win_event_hook_handle=None,
        event_id=None,
        hwnd=None,
        id_object=None,
        id_child=None,
        event_thread_id=None,
        event_time_ms=None,
        ):
    global is_ao_focus
    window_title = get_window_title(hwnd)

    if window_title in IGNORED_TITLES:
        return
    print(' - '+window_title)

    if window_title == AO_TITLE:
        is_ao_focus = True
        set_cursor_size(SIZE_CUSTOM)
        return
    if is_ao_focus and window_title != AO_TITLE:
        is_ao_focus = False
        set_cursor_size(SIZE_DEFAULT)
        return


def start_hook():
    global hook
    on_event(hwnd=win32gui.GetForegroundWindow())
    with init_com(), post_quit_message_on_break_signal():
        hook = set_win_event_hook(on_event, HookEvent.SYSTEM_FOREGROUND)

        try:
            run_message_loop()
        finally:
            hook.unhook()



## MAIN CONTROL ##

def start_main():
    tray.thread.start()
    start_hook()

def stop_main():
    set_cursor_size(SIZE_DEFAULT)
    hook.unhook()
    os._exit(0)


if __name__ == "__main__":
    keyboard.add_hotkey('shift+x', stop_main)
    tray = Tray(
        exit_callback=stop_main,
        size_callback=set_cursor_size,
        )
    start_main()
