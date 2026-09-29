import sys

from PySide6.QtWidgets import QApplication

from menu import MenuWindow
from single_player import SinglePlayerWindow
from two_player import TwoPlayerWindow


class AppController:
    """Ana menü <-> 1 oyunculu <-> 2 oyunculu geçişlerini yönetir."""

    def __init__(self, app):
        self.app = app
        self.window = None
        self.fullscreen = True

        # Eski pencereleri hemen yok etmiyoruz; bekleyen
        # timer'lar olabilir ve sinyal içinde silinmesin diye.
        self._retired = []

    def switch_to(self, new_window):
        old = self.window

        if old is not None:
            self.fullscreen = old.isFullScreen()

        self.window = new_window

        if self.fullscreen:
            new_window.showFullScreen()
        else:
            new_window.show()

        if old is not None:
            old.hide()
            self._retired.append(old)

    def show_menu(self):
        self.switch_to(
            MenuWindow(
                self.start_single,
                self.start_two,
                self.app.quit,
            )
        )

    def start_single(self):
        self.switch_to(SinglePlayerWindow(self.show_menu))

    def start_two(self):
        self.switch_to(TwoPlayerWindow(self.show_menu))


def main():
    app = QApplication(sys.argv)

    controller = AppController(app)
    controller.show_menu()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
