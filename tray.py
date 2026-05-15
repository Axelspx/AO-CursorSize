import threading
import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image
import settings



class Tray:
    def __init__(self, exit_callback, size_callback):
        self.exit_callback = exit_callback
        self.size_callback = size_callback
        self.icon_path = Image.open("Icons/Cursor.png")
        self.icon = pystray.Icon(
            "AO Cursor",
            icon = self.icon_path,
            title = "AO Cursor",
            )
        self.thread = threading.Thread(target=self.start_tray, daemon=True)


    def start_tray(self):
        self.icon.menu = self.build_menu()
        self.icon.run() #!THREAD BECOMES OCCUPIED HERE

    def stop_tray(self):
        self.icon.stop()
        self.exit_callback()


    def on_select_size(self, size:int=32, icon=None, item=None):
        settings.selected_size = size
        self.icon.menu = self.build_menu()

    def is_selected_size(self, size:int) -> bool:
        return settings.selected_size == size

    def menu_item(self, label:str, size:int) -> Item:
        return Item(
            label,
            lambda: self.on_select_size(size),
            checked=lambda item: self.is_selected_size(size),
            )

    def build_menu(self) -> Menu:
        size_menu = Menu(
            self.menu_item('x0.75', 24),
            self.menu_item('x1 (default)', 32),
            self.menu_item('x1.125', 36),
            self.menu_item('x1.25', 40),
            self.menu_item('x1.375', 44),
            self.menu_item('x1.5', 48),
            self.menu_item('x2', 64),
            )
        return Menu(
            Item('Cursor sizes', size_menu),
            pystray.Menu.SEPARATOR,
            Item('Exit', self.stop_tray),
            )