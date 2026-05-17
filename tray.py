import threading
import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image
import settings
from settings import (
    is_startup, set_startup,
    get_data_path,
    TITLE, cycle_cursor_icon, get_cursor_icon,
    save_reg, CURSOR_REG, SIZE_REG,
    debug_print,
    )



class Tray:
    def __init__(self, exit_callback) -> None:
        self.exit_callback = exit_callback
        self.icon = pystray.Icon(
            TITLE,
            icon = Image.open(get_data_path(f"Icons/{get_cursor_icon()}")),
            title = TITLE,
            )
        self.thread = threading.Thread(target=self.start_tray, daemon=True)


    ## TRAY CONTROL ##
    def start_tray(self) -> None:
        # Set tray icon menu, run tray process
        self.icon.menu = self.build_menu()
        self.icon.run()

    def stop_tray(self) -> None:
        # Stop tray process, exit callback to main
        self.icon.stop()
        self.exit_callback()

    def set_icon(self, img_path) -> None:
        # Update tray icon to passed img path
        self.icon.icon = Image.open(get_data_path(f"Icons/{img_path}"))
        debug_print(f"Set icon to: {img_path}")


    ## MENU ##
    def on_click_icon(self) -> None:
        # Cycle cursor index and update icon to correspond
        debug_print(f"Icon clicked: cursor_index is currently = {settings.cursor_index}")
        cycle_cursor_icon()
        self.set_icon(get_cursor_icon())
        save_reg(CURSOR_REG, settings.cursor_index)

    def on_select_size(self, size:int=32) -> None:
        # Set selected size value to passed size value, update tray menu
        settings.selected_size = size
        save_reg(SIZE_REG, settings.selected_size)
        debug_print(f"Set selected size {size}")
        self.icon.menu = self.build_menu()

    def is_selected_size(self, size:int) -> bool:
        # Check passed size is matching current selected size setting, return result
        return settings.selected_size == size

    def toggle_startup(self) -> None:
        # Startup on/off switch, update tray menu
        value = not is_startup()
        set_startup(value)
        self.icon.menu = self.build_menu()

    def build_menu(self) -> Menu:
        def menu_item(label:str, size:int) -> Item:
            return Item(
                label,
                lambda icon, item: self.on_select_size(size),
                checked=lambda item: self.is_selected_size(size),
            )
        size_menu = Menu(
            menu_item('x0.75', 24),
            menu_item('x1 (default)', 32),
            menu_item('x1.125', 36),
            menu_item('x1.25', 40),
            menu_item('x1.375', 44),
            menu_item('x1.5', 48),
            menu_item('x2', 64),
            )
        return Menu(
            Item('Set in-game size', size_menu),
            pystray.Menu.SEPARATOR,
            Item('Launch on startup', self.toggle_startup, checked=lambda item: is_startup()),
            Item('Exit', self.stop_tray),
            Item('Left-Click-Item', lambda icon, item:self.on_click_icon(), default=True, visible=False)
            )
