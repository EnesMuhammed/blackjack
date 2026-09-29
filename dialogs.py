from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from blackjack import BetDialog


MENU_CODE = 2


MENU_BUTTON_STYLE = """
QPushButton#menu_button {
    color: #c8ddd4;
    background: #172b23;

    border: 1px solid #345548;
    border-radius: 12px;

    padding: 10px 18px;

    font-size: 14px;
    font-weight: 800;
}

QPushButton#menu_button:hover {
    color: #e6c566;
    background: #214035;
    border: 1px solid #d8b45a;
}
"""


DIALOG_EXTRA_STYLE = """
QLabel#dialog_player {
    color: #d8e9e1;
    font-size: 14px;
    font-weight: 900;
}

QPushButton#dialog_menu {
    min-height: 34px;
    max-height: 34px;

    padding: 0px 16px;

    color: #9bbcaf;
    background: #17251f;

    border: 1px solid #263d35;

    font-size: 12px;
    font-weight: 800;
}

QPushButton#dialog_menu:hover {
    color: #e6c566;
    background: #214035;
    border: 1px solid #d8b45a;
}
"""


class MenuBetDialog(BetDialog):
    """
    Orijinal BetDialog + 'MAIN MENU' butonu (+ opsiyonel oyuncu başlığı).
    Esc / pencereyi kapatma ile diyalog kapanmaz; çıkış için
    ya bahis verilir ya da MAIN MENU'ya basılır.
    """

    def __init__(
        self,
        balance,
        result_text,
        profit,
        parent=None,
        player_name=None,
    ):
        super().__init__(
            balance,
            result_text,
            profit,
            parent,
        )

        layout = self.layout()

        extra_height = 50

        if player_name:
            header = QLabel(player_name)
            header.setObjectName("dialog_player")
            header.setAlignment(Qt.AlignCenter)

            layout.insertWidget(0, header)

            extra_height += 32

            self.setWindowTitle(f"{player_name} • New Round")

        self.menu_button = QPushButton("MAIN MENU")
        self.menu_button.setObjectName("dialog_menu")
        self.menu_button.setAutoDefault(False)
        self.menu_button.setDefault(False)
        self.menu_button.setFocusPolicy(Qt.NoFocus)
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(
            lambda checked=False: self.done(MENU_CODE)
        )

        layout.addWidget(self.menu_button)

        self.setFixedSize(480, 390 + extra_height)

        self.setStyleSheet(
            self.styleSheet() + DIALOG_EXTRA_STYLE
        )

    def reject(self):
        # Esc ile yanlışlıkla kapanmasın.
        pass


# =========================================================
# 2 OYUNCULU ORTAK BAHİS DİYALOĞU
# =========================================================

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class BetPanel(QWidget):
    """BetDialog'un tek oyunculuk içeriğinin aynısı (widget olarak)."""

    PRESET_BETS = BetDialog.PRESET_BETS

    changed = Signal()

    def __init__(self, name, balance, result_text, profit, parent=None):
        super().__init__(parent)

        self.balance = balance
        self.selected_bet = None
        self.active = balance > 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header = QLabel(name)
        header.setObjectName("dialog_player")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        result_label = QLabel(
            result_text if self.active else "OUT OF CHIPS"
        )
        result_label.setObjectName("dialog_result")
        result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(result_label)

        if profit > 0:
            profit_text = f"+${profit:,}"
        elif profit < 0:
            profit_text = f"-${abs(profit):,}"
        else:
            profit_text = "$0"

        profit_label = QLabel(profit_text)
        profit_label.setObjectName("dialog_profit")
        profit_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(profit_label)

        balance_label = QLabel(f"BALANCE  ${balance:,}")
        balance_label.setObjectName("dialog_balance")
        balance_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(balance_label)

        section = QLabel("SELECT BET")
        section.setObjectName("dialog_section")
        section.setAlignment(Qt.AlignCenter)
        layout.addWidget(section)

        self.preset_buttons = []

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(7)

        for index, amount in enumerate(self.PRESET_BETS):
            button = QPushButton(f"${amount}")
            button.setCheckable(True)
            button.setObjectName("preset_button")
            button.setFixedHeight(40)
            button.setEnabled(amount <= balance)
            button.clicked.connect(
                lambda checked=False, value=amount:
                self.select_amount(value)
            )

            self.preset_buttons.append((amount, button))
            grid.addWidget(button, index // 3, index % 3)

        layout.addLayout(grid)

        row = QHBoxLayout()
        row.setSpacing(8)

        self.minus_button = QPushButton("−")
        self.minus_button.setObjectName("amount_button")
        self.minus_button.setFixedSize(46, 42)

        self.amount_entry = QLineEdit()
        self.amount_entry.setObjectName("amount_entry")
        self.amount_entry.setAlignment(Qt.AlignCenter)
        self.amount_entry.setPlaceholderText("Amount")
        self.amount_entry.setFixedHeight(42)
        self.amount_entry.setValidator(
            QIntValidator(1, max(1, balance))
        )

        self.plus_button = QPushButton("+")
        self.plus_button.setObjectName("amount_button")
        self.plus_button.setFixedSize(46, 42)

        row.addWidget(self.minus_button)
        row.addWidget(self.amount_entry, stretch=1)
        row.addWidget(self.plus_button)

        layout.addLayout(row)

        self.minus_button.clicked.connect(self.decrease_amount)
        self.plus_button.clicked.connect(self.increase_amount)
        self.amount_entry.textChanged.connect(self.entry_changed)

        if not self.active:
            for _, button in self.preset_buttons:
                button.setEnabled(False)

            self.minus_button.setEnabled(False)
            self.plus_button.setEnabled(False)
            self.amount_entry.setEnabled(False)
            return

        available = [a for a, _ in self.preset_buttons if a <= balance]

        if available:
            self.select_amount(100 if 100 in available else available[-1])
        else:
            self.select_amount(balance)

    # -----------------------------------------------------

    def select_amount(self, amount):
        if not self.active:
            return

        amount = max(1, min(amount, self.balance))

        self.amount_entry.setText(str(amount))

    def entry_changed(self, text):
        amount = None

        if text:
            try:
                value = int(text)

                if 0 < value <= self.balance:
                    amount = value

            except ValueError:
                pass

        self.selected_bet = amount

        for preset, button in self.preset_buttons:
            button.setChecked(
                amount is not None
                and preset == amount
                and preset <= self.balance
            )

        self.changed.emit()

    def get_amount(self):
        try:
            return int(self.amount_entry.text())
        except ValueError:
            return None

    def decrease_amount(self):
        current = self.get_amount()

        if current is None:
            current = 20

        self.select_amount(max(1, current - 10))

    def increase_amount(self):
        current = self.get_amount()

        if current is None:
            current = 0

        if current >= self.balance:
            return

        self.select_amount(min(self.balance, current + 10))

    def is_ready(self):
        return (not self.active) or self.selected_bet is not None


DUAL_STYLE = """
QDialog {
    background: #0b1b15;
    border: 1px solid #146547;
}

QFrame#dialog_divider {
    background: #146547;
    min-width: 1px;
    max-width: 1px;
}

QLabel#dialog_result {
    color: #e6c566;
    font-size: 21px;
    font-weight: 800;
}

QLabel#dialog_profit {
    color: #ffffff;
    font-size: 28px;
    font-weight: 900;
}

QLabel#dialog_balance {
    color: #9bbcaf;
    font-size: 13px;
    font-weight: 700;
}

QLabel#dialog_section {
    color: #9bbcaf;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
}

QPushButton {
    border: none;
    border-radius: 9px;
    font-weight: 800;
}

QPushButton#preset_button {
    min-height: 40px;
    max-height: 40px;
    padding: 0px 12px;
    color: #c8ddd4;
    background: #172b23;
    border: 1px solid #345548;
    font-size: 13px;
    font-weight: 800;
}

QPushButton#preset_button:hover {
    background: #214035;
    border: 1px solid #d8b45a;
}

QPushButton#preset_button:checked {
    color: #07130f;
    background: #d8b45a;
    border: 1px solid #e6c566;
}

QPushButton#preset_button:disabled {
    color: #45564f;
    background: #101b17;
    border: 1px solid #1d2b25;
}

QPushButton#amount_button {
    min-width: 46px;
    max-width: 46px;
    min-height: 42px;
    max-height: 42px;
    padding: 0px;
    color: #d8e9e1;
    background: #263d35;
    font-size: 18px;
    font-weight: 800;
}

QPushButton#amount_button:hover {
    background: #345548;
}

QPushButton#amount_button:disabled {
    color: #45564f;
    background: #101b17;
}

QLineEdit#amount_entry {
    min-height: 42px;
    max-height: 42px;
    padding: 0px 12px;
    color: #e6c566;
    background: #07130f;
    border: 1px solid #345548;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 800;
}

QLineEdit#amount_entry:focus {
    border: 1px solid #d8b45a;
}

QLineEdit#amount_entry:disabled {
    background: #0b1b15;
    border: 1px solid #1d2b25;
}

QPushButton#dialog_new_game {
    min-height: 42px;
    max-height: 42px;
    padding: 0px 20px;
    color: #07130f;
    background: #d8b45a;
    font-size: 13px;
    font-weight: 900;
}

QPushButton#dialog_new_game:hover {
    background: #e6c566;
}

QPushButton#dialog_new_game:disabled {
    color: #61746d;
    background: #17251f;
}
""" + DIALOG_EXTRA_STYLE


class DualBetDialog(QDialog):
    """
    İki oyuncunun bahsini tek pencerede alır:
    solda Player 1, sağda Player 2, altta tek NEW GAME butonu.
    """

    def __init__(self, seats, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Round")
        self.setModal(True)
        self.setFixedSize(960, 500)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(28)

        self.panels = []

        for index, seat in enumerate(seats):
            panel = BetPanel(
                seat.name,
                seat.balance,
                seat.last_result or "PLACE YOUR BET",
                seat.last_profit,
            )

            panel.changed.connect(self.update_state)
            panel.amount_entry.returnPressed.connect(self.submit)

            self.panels.append(panel)

            row.addWidget(panel, 1)

            if index == 0:
                divider = QFrame()
                divider.setObjectName("dialog_divider")
                row.addWidget(divider)

        root.addLayout(row)

        self.new_game_button = QPushButton("NEW GAME")
        self.new_game_button.setObjectName("dialog_new_game")
        self.new_game_button.setFixedHeight(42)
        self.new_game_button.clicked.connect(self.submit)
        root.addWidget(self.new_game_button)

        self.menu_button = QPushButton("MAIN MENU")
        self.menu_button.setObjectName("dialog_menu")
        self.menu_button.setAutoDefault(False)
        self.menu_button.setDefault(False)
        self.menu_button.setFocusPolicy(Qt.NoFocus)
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(
            lambda checked=False: self.done(MENU_CODE)
        )
        root.addWidget(self.menu_button)

        self.setStyleSheet(DUAL_STYLE)

        self.update_state()

    def update_state(self):
        any_active = any(p.active for p in self.panels)

        self.new_game_button.setEnabled(
            any_active and all(p.is_ready() for p in self.panels)
        )

    def submit(self):
        if not self.new_game_button.isEnabled():
            return

        self.accept()

    def bets(self):
        return {
            index: panel.selected_bet
            for index, panel in enumerate(self.panels)
            if panel.active and panel.selected_bet is not None
        }

    def reject(self):
        # Esc ile yanlışlıkla kapanmasın.
        pass
