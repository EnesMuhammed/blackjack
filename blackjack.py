import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from game import BlackjackGame


BASE_DIR = Path(__file__).resolve().parent
CARDS_DIR = BASE_DIR / "assets" / "cards"


# =========================================================
# CARD
# =========================================================
class CardLabel(QLabel):
    SUIT_NAMES = {
        "S": "Spades",
        "H": "Hearts",
        "D": "Diamonds",
        "C": "Clubs",
    }

    RANK_NAMES = {
        "A": "Ace",
        "J": "Jack",
        "Q": "Queen",
        "K": "King",
    }

    def __init__(self, card_name="", parent=None):
        super().__init__(parent)

        self.card_name = card_name

        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(90, 130)
        self.setObjectName("card")

        if card_name:
            self.set_card(card_name)

    def set_card(self, card_name):
        self.card_name = card_name

        if card_name == "back":
            filename = "back.png"

        else:
            rank = card_name[:-1]
            suit = card_name[-1]

            suit_name = self.SUIT_NAMES.get(suit)

            if suit_name is None:
                self.setPixmap(QPixmap())
                self.setText("🂠")
                return

            rank_name = self.RANK_NAMES.get(
                rank,
                rank
            )

            filename = f"{rank_name}{suit_name}.png"

        path = CARDS_DIR / filename

        if path.exists():
            pixmap = QPixmap(str(path))

            if not pixmap.isNull():
                self.setPixmap(
                    pixmap.scaled(
                        110,
                        160,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
                return

        self.setPixmap(QPixmap())
        self.setText("🂠")
# =========================================================
# BET DIALOG
# =========================================================

class BetDialog(QDialog):
    PRESET_BETS = (
        20,
        50,
        100,
        200,
        500,
        1000,
    )

    def __init__(
        self,
        balance,
        result_text,
        profit,
        parent=None,
    ):
        super().__init__(parent)

        self.balance = balance
        self.selected_bet = None

        self.setWindowTitle("New Round")
        self.setModal(True)
        self.setFixedSize(480, 390)

        self.setup_ui(
            result_text,
            profit,
        )

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self, result_text, profit):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            28,
            22,
            28,
            22,
        )

        layout.setSpacing(10)

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        result_label = QLabel(result_text)

        result_label.setObjectName(
            "dialog_result"
        )

        result_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(result_label)

        # -------------------------------------------------
        # PROFIT
        # -------------------------------------------------

        if profit > 0:
            profit_text = f"+${profit:,}"

        elif profit < 0:
            profit_text = f"-${abs(profit):,}"

        else:
            profit_text = "$0"

        profit_label = QLabel(profit_text)

        profit_label.setObjectName(
            "dialog_profit"
        )

        profit_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(profit_label)

        # -------------------------------------------------
        # BALANCE
        # -------------------------------------------------

        balance_label = QLabel(
            f"BALANCE  ${self.balance:,}"
        )

        balance_label.setObjectName(
            "dialog_balance"
        )

        balance_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(balance_label)

        # -------------------------------------------------
        # PRESET BETS
        # -------------------------------------------------

        preset_title = QLabel(
            "SELECT BET"
        )

        preset_title.setObjectName(
            "dialog_section"
        )

        preset_title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(preset_title)

        self.preset_buttons = []

        preset_grid = QGridLayout()

        preset_grid.setHorizontalSpacing(8)
        preset_grid.setVerticalSpacing(7)

        for index, amount in enumerate(
            self.PRESET_BETS
        ):
            button = QPushButton(
                f"${amount}"
            )

            button.setCheckable(True)
            button.setObjectName(
                "preset_button"
            )

            button.setFixedHeight(40)

            button.setEnabled(
                amount <= self.balance
            )

            button.clicked.connect(
                lambda checked=False,
                value=amount:
                self.select_preset(value)
            )

            self.preset_buttons.append(
                button
            )

            row = index // 3
            column = index % 3

            preset_grid.addWidget(
                button,
                row,
                column,
            )

        layout.addLayout(
            preset_grid
        )

        # -------------------------------------------------
        # CUSTOM BET
        # -------------------------------------------------

        amount_row = QHBoxLayout()

        amount_row.setSpacing(8)

        self.minus_button = QPushButton("−")

        self.minus_button.setObjectName(
            "amount_button"
        )

        self.minus_button.setFixedSize(
            46,
            42,
        )

        self.amount_entry = QLineEdit()
        self.amount_entry.returnPressed.connect(self.submit)

        self.amount_entry.setObjectName(
            "amount_entry"
        )

        self.amount_entry.setAlignment(
            Qt.AlignCenter
        )

        self.amount_entry.setPlaceholderText(
            "Amount"
        )

        self.amount_entry.setFixedHeight(
            42
        )

        self.amount_entry.setValidator(
            QIntValidator(
                1,
                max(1, self.balance),
            )
        )

        self.plus_button = QPushButton("+")
        self.plus_button.setObjectName(
            "amount_button"
        )

        self.plus_button.setFixedSize(
            46,
            42,
        )

        amount_row.addWidget(
            self.minus_button
        )

        amount_row.addWidget(
            self.amount_entry,
            stretch=1,
        )

        amount_row.addWidget(
            self.plus_button
        )

        layout.addLayout(
            amount_row
        )

        # -------------------------------------------------
        # NEW GAME
        # -------------------------------------------------

        self.new_game_button = QPushButton(
            "NEW GAME"
        )

        self.new_game_button.setObjectName(
            "dialog_new_game"
        )

        self.new_game_button.setFixedHeight(
            42
        )

        self.new_game_button.setEnabled(
            False
        )

        layout.addWidget(
            self.new_game_button
        )

        # -------------------------------------------------
        # CONNECTIONS
        # -------------------------------------------------

        self.minus_button.clicked.connect(
            self.decrease_amount
        )

        self.plus_button.clicked.connect(
            self.increase_amount
        )

        self.amount_entry.textChanged.connect(
            self.entry_changed
        )

        self.new_game_button.clicked.connect(
            self.submit
        )

        # -------------------------------------------------
        # STYLE
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QDialog {
                background: #0b1b15;
                border: 1px solid #146547;
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
            """
        )

        self.select_initial_bet()

    # =====================================================
    # BET SELECTION
    # =====================================================

    def select_initial_bet(self):
        available = [
            amount
            for amount in self.PRESET_BETS
            if amount <= self.balance
        ]

        for button in self.preset_buttons:
            amount = int(
                button.text().replace("$", "")
            )

            button.setEnabled(
                amount <= self.balance
            )

            button.setChecked(False)

        self.selected_bet = None

        if available:
            if 100 in available:
                default_bet = 100
            else:
                default_bet = available[-1]

            self.select_preset(
                default_bet
            )

        elif self.balance > 0:
            self.set_amount(
                self.balance
            )

    def select_preset(self, amount):
        if amount <= 0:
            return

        if amount > self.balance:
            return

        self.selected_bet = amount

        for button in self.preset_buttons:
            preset_amount = int(
                button.text().replace("$", "")
            )

            button.setEnabled(
                preset_amount <= self.balance
            )

            button.setChecked(
                preset_amount == amount
                and preset_amount <= self.balance
            )

        self.amount_entry.setText(
            str(amount)
        )

        self.new_game_button.setEnabled(
            True
        )

    def set_amount(self, amount):
        if self.balance <= 0:
            self.selected_bet = None
            self.amount_entry.clear()
            self.new_game_button.setEnabled(
                False
            )
            return

        amount = max(
            1,
            min(
                amount,
                self.balance,
            ),
        )

        self.selected_bet = amount

        for button in self.preset_buttons:
            preset_amount = int(
                button.text().replace("$", "")
            )

            button.setEnabled(
                preset_amount <= self.balance
            )

            button.setChecked(
                preset_amount == amount
                and preset_amount <= self.balance
            )

        self.amount_entry.setText(
            str(amount)
        )

        self.new_game_button.setEnabled(
            True
        )

    def entry_changed(self, text):
        if not text:
            self.selected_bet = None

            for button in self.preset_buttons:
                button.setChecked(False)

            self.new_game_button.setEnabled(
                False
            )

            return

        try:
            amount = int(text)

        except ValueError:
            self.selected_bet = None
            self.new_game_button.setEnabled(
                False
            )
            return

        if amount <= 0:
            self.selected_bet = None
            self.new_game_button.setEnabled(
                False
            )
            return

        if amount > self.balance:
            self.selected_bet = None

            for button in self.preset_buttons:
                button.setChecked(False)

            self.new_game_button.setEnabled(
                False
            )

            return

        self.selected_bet = amount

        for button in self.preset_buttons:
            preset_amount = int(
                button.text().replace("$", "")
            )

            button.setChecked(
                preset_amount == amount
                and preset_amount <= self.balance
            )

        self.new_game_button.setEnabled(
            True
        )

    # =====================================================
    # +/- BUTTONS
    # =====================================================

    def decrease_amount(self):
        current = self.get_amount()

        if current is None:
            current = 20

        self.set_amount(
            max(
                1,
                current - 10,
            )
        )

    def increase_amount(self):
        current = self.get_amount()

        if current is None:
            current = 0

        if current >= self.balance:
            return

        self.set_amount(
            min(
                self.balance,
                current + 10,
            )
        )

    def get_amount(self):
        try:
            return int(
                self.amount_entry.text()
            )

        except ValueError:
            return None

    # =====================================================
    # SUBMIT
    # =====================================================

    def submit(self):
        amount = self.get_amount()

        if amount is None:
            return

        if amount <= 0:
            return

        if amount > self.balance:
            return

        self.selected_bet = amount

        self.accept()

    # =====================================================
    # RESULT
    # =====================================================

    def bet(self):
        return self.selected_bet


# =========================================================
# MAIN WINDOW
# =========================================================

class BlackjackWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Blackjack"
        )

        self.setMinimumSize(
            1100,
            700,
        )

        self.game = BlackjackGame(
            1000
        )

        # Animasyon durumları
        self.deal_animation_index = 0

        self.dealer_animation_index = 0

        self.hit_animation_pending = False

        self.dealer_animation_started = False

        self.setup_ui()

        self.show_bet_dialog(
            "PLACE YOUR BET",
            0,
        )

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):
        central = QWidget()

        central.setObjectName(
            "central"
        )

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            40,
            30,
            40,
            30,
        )

        main_layout.setSpacing(
            20
        )

        # -------------------------------------------------
        # TOP
        # -------------------------------------------------

        top_bar = QHBoxLayout()

        title = QLabel(
            "BLACKJACK"
        )

        title.setObjectName(
            "title"
        )

        self.balance_label = QLabel(
            "BALANCE   $1,000"
        )

        self.balance_label.setObjectName(
            "balance"
        )

        top_bar.addWidget(
            title
        )

        top_bar.addStretch()

        top_bar.addWidget(
            self.balance_label
        )

        main_layout.addLayout(
            top_bar
        )

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        table = QFrame()

        table.setObjectName(
            "table"
        )

        table_layout = QVBoxLayout(
            table
        )

        table_layout.setContentsMargins(
            50,
            35,
            50,
            35,
        )

        table_layout.setSpacing(
            10
        )

        # -------------------------------------------------
        # DEALER
        # -------------------------------------------------

        dealer_title = QLabel(
            "DEALER"
        )

        dealer_title.setObjectName(
            "section_title"
        )

        dealer_title.setAlignment(
            Qt.AlignCenter
        )

        table_layout.addWidget(
            dealer_title
        )

        self.dealer_value_label = QLabel(
            ""
        )

        self.dealer_value_label.setObjectName(
            "hand_value"
        )

        self.dealer_value_label.setAlignment(
            Qt.AlignCenter
        )

        table_layout.addWidget(
            self.dealer_value_label
        )

        self.dealer_cards_layout = QHBoxLayout()

        self.dealer_cards_layout.setAlignment(
            Qt.AlignCenter
        )

        self.dealer_cards_layout.setSpacing(
            4
        )

        table_layout.addLayout(
            self.dealer_cards_layout
        )

        table_layout.addStretch()

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status_label = QLabel(
            "PLACE YOUR BET"
        )

        self.status_label.setObjectName(
            "status"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        table_layout.addWidget(
            self.status_label
        )

        table_layout.addStretch()

        # -------------------------------------------------
        # PLAYER
        # -------------------------------------------------

        self.player_cards_layout = QHBoxLayout()

        self.player_cards_layout.setAlignment(
            Qt.AlignCenter
        )

        self.player_cards_layout.setSpacing(
            4
        )

        table_layout.addLayout(
            self.player_cards_layout
        )

        player_title = QLabel(
            "PLAYER"
        )

        player_title.setObjectName(
            "section_title"
        )

        player_title.setAlignment(
            Qt.AlignCenter
        )

        table_layout.addWidget(
            player_title
        )

        self.player_value_label = QLabel(
            ""
        )

        self.player_value_label.setObjectName(
            "hand_value"
        )

        self.player_value_label.setAlignment(
            Qt.AlignCenter
        )

        table_layout.addWidget(
            self.player_value_label
        )

        main_layout.addWidget(
            table,
            stretch=1,
        )

        # -------------------------------------------------
        # ACTION BAR
        # -------------------------------------------------

        bottom_bar = QHBoxLayout()

        bottom_bar.setSpacing(
            12
        )

        self.hit_button = QPushButton(
            "HIT"
        )

        self.hit_button.setObjectName(
            "hit_button"
        )

        self.stand_button = QPushButton(
            "STAND"
        )

        self.stand_button.setObjectName(
            "stand_button"
        )

        bottom_bar.addWidget(
            self.hit_button
        )

        bottom_bar.addWidget(
            self.stand_button
        )

        main_layout.addLayout(
            bottom_bar
        )

        # -------------------------------------------------
        # SIGNALS
        # -------------------------------------------------

        self.hit_button.clicked.connect(
            self.hit
        )

        self.stand_button.clicked.connect(
            self.stand
        )

        # -------------------------------------------------
        # STYLE
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QMainWindow {
                background: #07130f;
            }

            QWidget#central {
                background: #07130f;
            }

            QLabel#title {
                color: white;
                font-size: 30px;
                font-weight: 800;
                letter-spacing: 2px;
            }

            QLabel#balance {
                color: #d8b45a;
                background: #101f19;

                border: 1px solid #263d35;
                border-radius: 12px;

                padding: 10px 18px;

                font-size: 16px;
                font-weight: 700;
            }

            QFrame#table {
                background: #0b4a35;

                border: 1px solid #146547;
                border-radius: 30px;
            }

            QLabel#section_title {
                color: #9bbcaf;

                font-size: 15px;
                font-weight: 700;

                letter-spacing: 2px;
            }

            QLabel#hand_value {
                color: #d8e9e1;

                font-size: 14px;
                font-weight: 600;
            }

            QLabel#card {
                background: transparent;
            }

            QLabel#status {
                color: #e6c566;

                font-size: 19px;
                font-weight: 800;

                letter-spacing: 1px;
            }

            QPushButton {
                border: none;
                border-radius: 10px;

                padding: 12px 22px;

                font-size: 14px;
                font-weight: 800;
            }

            QPushButton#hit_button {
                color: white;
                background: #16865c;
            }

            QPushButton#hit_button:hover {
                background: #1b9b6b;
            }

            QPushButton#stand_button {
                color: white;
                background: #b83b4b;
            }

            QPushButton#stand_button:hover {
                background: #cc4859;
            }

            QPushButton:disabled {
                color: #61746d;
                background: #17251f;
            }
            """
        )

    # =====================================================
    # HIT
    # =====================================================

    def hit(self):
        if not self.game.can_hit:
            return

        success, result = self.game.hit()

        if not success:
            return

        self.hit_button.setEnabled(False)
        self.stand_button.setEnabled(False)

        self.hit_animation_pending = True

        QTimer.singleShot(
            180,
            lambda r=result:
            self.finish_hit_animation(r)
        )

    def finish_hit_animation(self, result):
        self.hit_animation_pending = False

        self.update_balance()
        self.update_player()

        # -------------------------------------------------
        # BUST
        # -------------------------------------------------

        if result == "BUST":
            self.hit_button.setEnabled(False)
            self.stand_button.setEnabled(False)

            self.status_label.setText(
                f"BUST • "
                f"{self.game.player_hand.value}"
            )

            QTimer.singleShot(
                1000,
                self.finish_round_popup
            )

            return

        # -------------------------------------------------
        # 21
        # -------------------------------------------------

        if result == "21":
            self.status_label.setText(
                "21!"
            )

            self.start_dealer_animation(
                reveal_delay=500
            )

            return

        # -------------------------------------------------
        # NORMAL
        # -------------------------------------------------

        self.hit_button.setEnabled(
            self.game.can_hit
        )

        self.stand_button.setEnabled(
            self.game.can_stand
        )

        self.status_label.setText(
            f"YOUR TURN  •  "
            f"{self.game.player_hand.value}"
        )

    # =====================================================
    # STAND
    # =====================================================

    def stand(self):
        if not self.game.can_stand:
            return

        success, _ = self.game.stand()

        if not success:
            return

        self.hit_button.setEnabled(False)
        self.stand_button.setEnabled(False)

        self.status_label.setText(
            "DEALER TURN..."
        )

        self.start_dealer_animation(
            reveal_delay=500
        )

    # =====================================================
    # INITIAL DEAL ANIMATION
    # =====================================================

    def start_initial_deal_animation(self):
        self.deal_animation_index = 0

        self.clear_layout(
            self.player_cards_layout
        )

        self.clear_layout(
            self.dealer_cards_layout
        )

        self.player_value_label.setText(
            ""
        )

        self.dealer_value_label.setText(
            ""
        )

        self.status_label.setText(
            "DEALING..."
        )

        self.hit_button.setEnabled(False)
        self.stand_button.setEnabled(False)

        QTimer.singleShot(
            250,
            self.animate_initial_deal
        )

    def animate_initial_deal(self):
        sequence = (
            ("player", 0),
            ("dealer", 0),
            ("player", 1),
            ("dealer", 1),
        )

        if (
            self.deal_animation_index
            >= len(sequence)
        ):
            self.finish_initial_deal_animation()
            return

        owner, index = sequence[
            self.deal_animation_index
        ]

        if owner == "player":
            card = (
                self.game
                .player_hand
                .cards[index]
            )

            self.player_cards_layout.addWidget(
                CardLabel(
                    card.image_name
                )
            )

            visible_cards = (
                self.game
                .player_hand
                .cards[:index + 1]
            )

            self.player_value_label.setText(
                str(
                    self.calculate_hand_value(
                        visible_cards
                    )
                )
            )

        else:
            card = (
                self.game
                .dealer_hand
                .cards[index]
            )

            if index == 1:
                label = CardLabel(
                    "back"
                )

            else:
                label = CardLabel(
                    card.image_name
                )

            self.dealer_cards_layout.addWidget(
                label
            )

            if index == 0:
                self.dealer_value_label.setText(
                    f"{card.value} + ?"
                )

        self.deal_animation_index += 1

        QTimer.singleShot(
            320,
            self.animate_initial_deal
        )

    def finish_initial_deal_animation(self):
        self.update_balance()

        # -------------------------------------------------
        # NATURAL BLACKJACK
        # -------------------------------------------------

        if self.game.round_finished:
            self.update_ui(
                reveal_dealer=True
            )

            self.status_label.setText(
                self.game.last_result
            )

            QTimer.singleShot(
                1200,
                self.finish_round_popup
            )

            return

        self.hit_button.setEnabled(
            self.game.can_hit
        )

        self.stand_button.setEnabled(
            self.game.can_stand
        )

        self.status_label.setText(
            f"YOUR TURN  •  "
            f"{self.game.player_hand.value}"
        )

    # =====================================================
    # DEALER ANIMATION
    # =====================================================

    def start_dealer_animation(
        self,
        reveal_delay=500,
    ):
        self.dealer_animation_index = 0
        self.dealer_animation_started = True

        self.clear_layout(
            self.dealer_cards_layout
        )

        self.dealer_value_label.setText(
            ""
        )

        # Önce mevcut ilk dealer kartını
        # gösteriyoruz.
        QTimer.singleShot(
            reveal_delay,
            self.animate_dealer_reveal
        )

    def animate_dealer_reveal(self):
        if not self.dealer_animation_started:
            return

        cards = (
            self.game
            .dealer_hand
            .cards
        )

        if not cards:
            self.end_dealer_animation()
            return

        # -------------------------------------------------
        # FIRST CARD
        # -------------------------------------------------

        first_card = cards[0]

        self.dealer_cards_layout.addWidget(
            CardLabel(
                first_card.image_name
            )
        )

        self.dealer_animation_index = 1

        self.dealer_value_label.setText(
            str(
                self.calculate_hand_value(
                    cards[:1]
                )
            )
        )

        # Hole card'ı açmadan önce kısa bekleme.
        QTimer.singleShot(
            500,
            self.animate_dealer_hole_card
        )

    def animate_dealer_hole_card(self):
        if not self.dealer_animation_started:
            return

        cards = (
            self.game
            .dealer_hand
            .cards
        )

        if len(cards) < 2:
            self.request_dealer_step()
            return

        # -------------------------------------------------
        # SECOND / HOLE CARD
        # -------------------------------------------------

        second_card = cards[1]

        self.dealer_cards_layout.addWidget(
            CardLabel(
                second_card.image_name
            )
        )

        self.dealer_animation_index = 2

        self.dealer_value_label.setText(
            str(
                self.calculate_hand_value(
                    cards[:2]
                )
            )
        )

        # Eğer dealer zaten 17+ ise
        # game.py dealer_step() sonucu bitirecek.
        QTimer.singleShot(
            500,
            self.request_dealer_step
        )

    def request_dealer_step(self):
        if not self.dealer_animation_started:
            return

        # Dealer turu bittiyse sonuç ekranına geç.
        if self.game.dealer_finished:
            self.end_dealer_animation()
            return

        success, result = (
            self.game.dealer_step()
        )

        if not success:
            self.dealer_animation_started = False

            self.status_label.setText(
                result
            )

            return

        # Eğer dealer_step FINISHED döndürdüyse,
        # çekilen son kartı göstermek için yine
        # animasyon fonksiyonuna geçiyoruz.
        self.animate_new_dealer_card()

    def animate_new_dealer_card(self):
        if not self.dealer_animation_started:
            return

        cards = (
            self.game
            .dealer_hand
            .cards
        )

        index = self.dealer_animation_index

        if index >= len(cards):
            if self.game.dealer_finished:
                self.end_dealer_animation()
            else:
                QTimer.singleShot(
                    500,
                    self.request_dealer_step
                )

            return

        card = cards[index]

        self.dealer_cards_layout.addWidget(
            CardLabel(
                card.image_name
            )
        )

        self.dealer_animation_index += 1

        visible_cards = cards[
            :self.dealer_animation_index
        ]

        self.dealer_value_label.setText(
            str(
                self.calculate_hand_value(
                    visible_cards
                )
            )
        )

        # Dealer bu karttan sonra bittiyse
        # final sonucu göster.
        if self.game.dealer_finished:
            QTimer.singleShot(
                500,
                self.end_dealer_animation
            )

            return

        # Bir sonraki dealer kartı için önce
        # 500 ms bekle, sonra gerçekten çek.
        QTimer.singleShot(
            500,
            self.request_dealer_step
        )

    def end_dealer_animation(self):
        if not self.dealer_animation_started:
            return

        self.dealer_animation_started = False

        self.dealer_value_label.setText(
            str(
                self.game
                .dealer_hand
                .value
            )
        )

        self.status_label.setText(
            self.game.last_result
        )

        # Sonucu oyuncunun görmesi için bekle.
        QTimer.singleShot(
            1200,
            self.finish_round_popup
        )

    # =====================================================
    # HAND VALUE
    # =====================================================

    @staticmethod
    def calculate_hand_value(cards):
        total = sum(
            card.value
            for card in cards
        )

        aces = sum(
            1
            for card in cards
            if card.rank == "A"
        )

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    # =====================================================
    # BET POPUP
    # =====================================================

    def show_bet_dialog(
        self,
        result_text,
        profit,
    ):
        if self.game.balance <= 0:
            self.status_label.setText(
                "GAME OVER • NO BALANCE"
            )

            self.hit_button.setEnabled(
                False
            )

            self.stand_button.setEnabled(
                False
            )

            return

        dialog = BetDialog(
            self.game.balance,
            result_text,
            profit,
            self,
        )

        if dialog.exec() == QDialog.Accepted:
            bet = dialog.bet()

            if bet is not None:
                self.start_new_round(
                    bet
                )

    def finish_round_popup(self):
        self.hit_button.setEnabled(
            False
        )

        self.stand_button.setEnabled(
            False
        )

        self.update_balance()

        self.show_bet_dialog(
            self.game.last_result,
            self.game.last_profit,
        )

    # =====================================================
    # NEW ROUND
    # =====================================================

    def start_new_round(self, bet):
        if bet <= 0:
            return

        if bet > self.game.balance:
            self.status_label.setText(
                "INSUFFICIENT BALANCE"
            )
            return

        success, result = (
            self.game.start_round(
                bet
            )
        )

        if not success:
            self.status_label.setText(
                self.error_text(result)
            )
            return

        self.start_initial_deal_animation()

    # =====================================================
    # UI UPDATE
    # =====================================================

    def update_ui(
        self,
        reveal_dealer=False,
    ):
        self.update_balance()

        self.update_dealer(
            reveal_dealer
        )

        self.update_player()

        self.hit_button.setEnabled(
            self.game.can_hit
        )

        self.stand_button.setEnabled(
            self.game.can_stand
        )

    def update_balance(self):
        self.balance_label.setText(
            f"BALANCE   "
            f"${self.game.balance:,}"
        )

    # =====================================================
    # DEALER
    # =====================================================

    def update_dealer(
        self,
        reveal=False,
    ):
        self.clear_layout(
            self.dealer_cards_layout
        )

        cards = (
            self.game
            .dealer_hand
            .cards
        )

        for index, card in enumerate(
            cards
        ):
            if (
                index == 1
                and not reveal
            ):
                label = CardLabel(
                    "back"
                )

            else:
                label = CardLabel(
                    card.image_name
                )

            self.dealer_cards_layout.addWidget(
                label
            )

        if reveal:
            self.dealer_value_label.setText(
                str(
                    self.game
                    .dealer_hand
                    .value
                )
            )

        elif cards:
            self.dealer_value_label.setText(
                f"{cards[0].value} + ?"
            )

        else:
            self.dealer_value_label.setText(
                ""
            )

    # =====================================================
    # PLAYER
    # =====================================================

    def update_player(self):
        self.clear_layout(
            self.player_cards_layout
        )

        for card in (
            self.game
            .player_hand
            .cards
        ):
            self.player_cards_layout.addWidget(
                CardLabel(
                    card.image_name
                )
            )

        if (
            self.game
            .player_hand
            .cards
        ):
            self.player_value_label.setText(
                str(
                    self.game
                    .player_hand
                    .value
                )
            )

        else:
            self.player_value_label.setText(
                ""
            )

    # =====================================================
    # HELPERS
    # =====================================================

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def error_text(self, error):
        messages = {
            "INVALID_BET":
                "INVALID BET",

            "INSUFFICIENT_BALANCE":
                "INSUFFICIENT BALANCE",

            "ROUND_ACTIVE":
                "ROUND ALREADY ACTIVE",

            "NO_ACTIVE_GAME":
                "NO ACTIVE GAME",

            "NO_DEALER_TURN":
                "NO DEALER TURN",
        }

        return messages.get(
            error,
            error,
        )

    # =====================================================
    # FULLSCREEN
    # =====================================================

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()

            else:
                self.showFullScreen()

        elif event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()

        else:
            super().keyPressEvent(event)


# =========================================================
# MAIN
# =========================================================

def main():
    app = QApplication(sys.argv)

    window = BlackjackWindow()

    window.showFullScreen()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
