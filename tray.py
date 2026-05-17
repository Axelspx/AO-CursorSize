import threading
import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image
import settings
from settings import save_selected_size, is_startup, set_startup, get_data_path, TITLE



class Tray:
    def __init__(self, exit_callback) -> None:
        self.exit_callback = exit_callback
        self.icon_path = Image.open(get_data_path("Icons/Cursor.png"))
        self.icon = pystray.Icon(
            TITLE,
            icon = self.icon_path,
            title = TITLE,
            )
        self.thread = threading.Thread(target=self.start_tray, daemon=True)


    def start_tray(self)-> None:
        self.icon.menu = self.build_menu()
        self.icon.run() #!THREAD BECOMES OCCUPIED HERE

    def stop_tray(self)-> None:
        self.icon.stop()
        self.exit_callback()

    def hide_tray(self):
        pass


    ## MENU ##
    def on_select_size(self, size:int=32, icon=None, item=None)-> None:
        settings.selected_size = size
        save_selected_size()
        self.icon.menu = self.build_menu()

    def is_selected_size(self, size:int) -> bool:
        return settings.selected_size == size

    def toggle_startup(self) -> None:
        value = not is_startup()
        set_startup(value)
        self.icon.menu = self.build_menu()

    def build_menu(self) -> Menu:
        def menu_item(label:str, size:int) -> Item:
            return Item(
                label,
                lambda: self.on_select_size(size),
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
            Item('Hide tray icon', self.hide_tray, enabled=False),
            Item('Launch on startup', self.toggle_startup, checked=lambda item: is_startup()),
            Item('Exit', self.stop_tray),
            )
