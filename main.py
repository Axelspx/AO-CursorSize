import win32gui
import keyboard
import os
from win32_window_monitor import *
import ctypes

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

AO_CLIENT = "Albion Online Client"
SIZE_0 = 16
SIZE_0_5 = 24
SIZE_1 = 32 # Windows default (Accessibility cursor size slider value 1)
SIZE_1_5 = 40
SIZE_2 = 48
SIZE_3 = 64
last_size = None
ao_client_focus = False
other_focus = False



def set_cursor_size(size) -> bool:
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
    global ao_client_focus
    window_title = get_window_title(hwnd)
    print(' - '+window_title)

    if window_title == AO_CLIENT:
        ao_client_focus = True
        set_cursor_size(SIZE_1_5)
        return
    if ao_client_focus and window_title != AO_CLIENT:
        ao_client_focus = False
        set_cursor_size(SIZE_1)
        return


def start_script():
    global hook
    on_event(hwnd=win32gui.GetForegroundWindow())
    with init_com(), post_quit_message_on_break_signal():
        hook = set_win_event_hook(on_event, HookEvent.SYSTEM_FOREGROUND)

        try:
            run_message_loop()
        finally:
            hook.unhook()



if __name__ == "__main__":
    def stop_script():
        set_cursor_size(SIZE_1)
        hook.unhook()
        os._exit(0)

    keyboard.add_hotkey('shift+x', stop_script)
    start_script()
