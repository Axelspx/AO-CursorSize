import win32gui
import keyboard
import os
from win32_window_monitor import *
import ctypes
from tray import Tray
import settings
from settings import (
    user32,
    SPI_SETCURSORSIZE, SPIF_UPDATEINIFILE, SPIF_SENDCHANGE,
    IGNORED_TITLES, SIZE_DEFAULT, AO_TITLE
    )




user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SystemParametersInfoW.restype = ctypes.c_bool
user32.SystemParametersInfoW.argtypes = [
    ctypes.c_uint,
    ctypes.c_uint,
    ctypes.c_void_p,
    ctypes.c_uint,
    ]






def set_cursor_size(size: int= settings.SIZE_DEFAULT) -> bool:


    if not size:
        size = settings.SIZE_DEFAULT
    if size == settings.current_size:
       return True

    print('Setting cursor size..')
    ok = user32.SystemParametersInfoW(
        settings.SPI_SETCURSORSIZE,
        0,
        ctypes.c_void_p(size),
        settings.SPIF_UPDATEINIFILE | settings.SPIF_SENDCHANGE,
        )

    if not ok:
        err = ctypes.get_last_error()
        print(f"SystemParametersInfoW failed, GetLastError={err}")
        return False
    print(f'Set cursor size to {size}')
    settings.current_size = size
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
    window_title = get_window_title(hwnd)
    print(f' [*] Event - Title: {window_title}, is_ao_focus: {settings.is_ao_focus}')

    if window_title in settings.IGNORED_TITLES:
        print('  - Ignored title')
        return
    print(' - '+window_title)
    if window_title == settings.AO_TITLE:
        is_ao_focus = True
        set_cursor_size(tray.selected_size)
        return
    if is_ao_focus and window_title != settings.AO_TITLE and current_size != settings.SIZE_DEFAULT:
        print(f'[*] Resetting cursor (is_ao_focus={is_ao_focus}, new_title={window_title})')
        is_ao_focus = False
        set_cursor_size(settings.SIZE_DEFAULT)
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
    set_cursor_size(settings.SIZE_DEFAULT)
    hook.unhook()
    os._exit(0)


if __name__ == "__main__":
    keyboard.add_hotkey('shift+x', stop_main)
    tray = Tray(
        exit_callback=stop_main,
        size_callback=set_cursor_size,
        )
    start_main()
