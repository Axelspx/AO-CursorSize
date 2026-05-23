import win32gui
import os
from win32_window_monitor import *
import ctypes
from tray import Tray
import settings
from settings import (
    USER32,
    SPI_SETCURSORSIZE, SPIF_UPDATEINIFILE, SPIF_SENDCHANGE,
    IGNORED_TITLES, SIZE_DEFAULT, AO_TITLE,
    load_reg, save_reg, SIZE_REG, CURSOR_REG, debug_print
    )

hook = None
event_count = 0


## MAIN ##
def set_cursor_size(size: int= SIZE_DEFAULT) -> bool:

    if not size:
        size = SIZE_DEFAULT
    if size == settings.current_size:
       return True

    debug_print('Setting cursor size..')
    ok = USER32.SystemParametersInfoW(
        SPI_SETCURSORSIZE,
        0,
        ctypes.c_void_p(size),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
        )

    if not ok:
        err = ctypes.get_last_error()
        debug_print(f"SystemParametersInfoW failed, Error: {err}")
        return False
    debug_print(f'Set cursor size to {size}')
    settings.current_size = size
    return True



def on_event( # foreground window change event
        win_event_hook_handle=None,
        event_id=None,
        hwnd=None,
        id_object=None,
        id_child=None,
        event_thread_id=None,
        event_time_ms=None,
        ) -> None:
    global event_count
    window_title = get_window_title(hwnd)
    event_count += 1
    debug_print(f' [{event_count}] Event - Title: {window_title}, is_ao_focus: {settings.is_ao_focus}')

    if window_title in IGNORED_TITLES:
        debug_print('  - Ignored title')
        return
    debug_print(' - '+window_title)
    if window_title == AO_TITLE:
        settings.is_ao_focus = True
        set_cursor_size(settings.selected_size)
        return
    if settings.is_ao_focus and window_title != AO_TITLE and settings.current_size != SIZE_DEFAULT:
        debug_print(f'[*] Resetting cursor (is_ao_focus={settings.is_ao_focus}, new_title={window_title})')
        settings.is_ao_focus = False
        set_cursor_size(SIZE_DEFAULT)
        return

def start_hook() -> None:
    global hook
    on_event(hwnd=win32gui.GetForegroundWindow())
    with init_com(), post_quit_message_on_break_signal():
        hook = set_win_event_hook(on_event, HookEvent.SYSTEM_FOREGROUND)
        try:
            run_message_loop()
        except Exception as e:
            debug_print(f"Message loop error: {e}")




## MAIN CONTROL ##
def initialize_settings() -> None:
    size = load_reg(SIZE_REG)
    cursor = load_reg(CURSOR_REG)
    settings.selected_size = size if size is not False else SIZE_DEFAULT
    settings.cursor_index = cursor if cursor is not False else 0
    debug_print("Initialized registry settings")

def start_main() -> None:
    tray.thread.start()
    start_hook()

def stop_main() -> None:
    if hook:
        hook.unhook() # type: ignore
    save_reg(SIZE_REG, settings.selected_size)
    save_reg(CURSOR_REG, settings.cursor_index)
    set_cursor_size(SIZE_DEFAULT)
    os._exit(0)

if __name__ == "__main__":
    initialize_settings()
    tray= Tray(exit_callback=stop_main)
    start_main()
