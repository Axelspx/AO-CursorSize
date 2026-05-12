import pywin32_system32
import psutil
import ctypes
import time
import win32gui
import keyboard
import pygetwindow as pygw
import winreg

DEFAULT_SIZE = 1
ALBION_SIZE = 2

running = True


def set_cursor_size(size):
    #! do this with pywinauto ??
    return

def check_foreground():
    while running:
        time.sleep(0.5)
        if is_ao_client():
            set_cursor_size(ALBION_SIZE)
        else:
            set_cursor_size(DEFAULT_SIZE)

def is_ao_client() -> bool:
    curr_window = pygw.getActiveWindow()
    if curr_window and hasattr(curr_window, 'title'):
        return curr_window.title == "Albion Online Client"
    return False



if __name__ == "__main__":
    def stop_script():
        global running
        running = False

    keyboard.add_hotkey('alt+x', lambda: set_cursor_size(2), suppress=True)
    keyboard.add_hotkey('alt+z', lambda: set_cursor_size(1), suppress=True)
    keyboard.add_hotkey('shift+x', stop_script, suppress=True)

    while running:
        time.sleep(0.1)
