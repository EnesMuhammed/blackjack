from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDialog, QPushButton

from blackjack import BlackjackWindow
from dialogs import MenuBetDialog, MENU_CODE, MENU_BUTTON_STYLE


class SinglePlayerWindow(BlackjackWindow):
    """
    Orijinal tek oyunculu oyun (blackjack.py) birebir aynı.
    Sadece:
      - sağ üste MENU butonu eklendi
      - bahis diyaloğuna MAIN MENU butonu eklendi
    """

    _ready = False
    _left = False

    def __init__(self, on_menu):
        super().__init__()

        self.on_menu = on_menu

        self._add_menu_button()

        self._ready = True

        QTimer.singleShot(0, self.begin)

    # -----------------------------------------------------

    def _add_menu_button(self):
        button = QPushButton("MENU")
        button.setObjectName("menu_button")
        button.setFocusPolicy(Qt.NoFocus)
        button.setCursor(Qt.PointingHandCursor)

        top_bar = (
            self.centralWidget()
            .layout()
            .itemAt(0)
            .layout()
        )

        top_bar.addSpacing(12)
        top_bar.addWidget(button)

        button.clicked.connect(self.go_menu)

        self.setStyleSheet(
            self.styleSheet() + MENU_BUTTON_STYLE
        )

    def begin(self):
        self.show_bet_dialog("PLACE YOUR BET", 0)

    def go_menu(self):
        if self._left:
            return

        self._left = True
        self.dealer_animation_started = False

        QTimer.singleShot(0, self.on_menu)

    # -----------------------------------------------------
    # Orijinal show_bet_dialog + menü desteği
    # -----------------------------------------------------

    def show_bet_dialog(self, result_text, profit):
        # __init__ sırasındaki erken çağrıyı ve menüden
        # çıkıldıktan sonra gelen eski timer'ları yok say.
        if not self._ready or self._left:
            return

        if self.game.balance <= 0:
            self.status_label.setText(
                "GAME OVER • NO BALANCE"
            )

            self.hit_button.setEnabled(False)
            self.stand_button.setEnabled(False)

            return

        dialog = MenuBetDialog(
            self.game.balance,
            result_text,
            profit,
            self,
        )

        code = dialog.exec()

        if code == MENU_CODE:
            self.go_menu()
            return

        if code == QDialog.Accepted:
            bet = dialog.bet()

            if bet is not None:
                self.start_new_round(bet)
