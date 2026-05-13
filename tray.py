import threading
import pystray
from pystray import MenuItem as Item, Menu



class Tray:
    def __init__(self, exit_callback, size_callback):
        self.exit_callback = exit_callback
        self.size_callback = size_callback

        self.icon_path = None
        self.icon = pystray.Icon("A", icon=self.icon_path, title="LetMeListen", )
        self.thread = threading.Thread(target=self.start, daemon=True)

    def start(self):
        self.icon.run()

    def stop(self):
        self.icon.stop()
        self.exit_callback()

    def on_size_menu(self):
        #TODO
        pass

    def build_menu(self):
        #TODO
        size_menu = Menu(
            Item('x0.75'),
            Item('x1 (default)'),
            Item('x1.125'),
            Item('x1.25'),
            Item('x1.5'),
            Item('x2'),
        )

        return Menu(
            Item('Cursor sizes', size_menu),
            pystray.Menu.SEPARATOR,
            Item('Exit', self.stop),
            #Item('Left-Click-Item', action=lambda:self.click_callback(), default=True, visible=False)
            )