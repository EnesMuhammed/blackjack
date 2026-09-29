from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from blackjack import BlackjackWindow, CardLabel
from dialogs import DualBetDialog, MENU_CODE, MENU_BUTTON_STYLE
from game2p import TwoPlayerBlackjackGame


calculate_hand_value = BlackjackWindow.calculate_hand_value


STYLE = (
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

    QLabel#balance[active="true"] {
        border: 1px solid #d8b45a;
    }

    QFrame#table {
        background: #0b4a35;

        border: 1px solid #146547;
        border-radius: 30px;
    }

    QFrame#divider {
        background: #146547;
        min-width: 1px;
        max-width: 1px;
    }

    QLabel#section_title {
        color: #9bbcaf;

        font-size: 15px;
        font-weight: 700;

        letter-spacing: 2px;
    }

    QLabel#section_title[active="true"] {
        color: #e6c566;
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
    + MENU_BUTTON_STYLE
)


class TwoPlayerWindow(QMainWindow):
    def __init__(self, on_menu):
        super().__init__()

        self.on_menu = on_menu
        self._left = False

        self.setWindowTitle("Blackjack • 2 Players")
        self.setMinimumSize(1100, 700)

        self.game = TwoPlayerBlackjackGame(1000)

        self.round_participants = []

        # Animasyon durumları
        self.deal_sequence = []
        self.deal_animation_index = 0
        self.dealer_animation_index = 0
        self.dealer_animation_started = False

        self.setup_ui()

        self.update_balances()

        QTimer.singleShot(0, self.collect_bets)

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # -------------------------------------------------
        # TOP
        # -------------------------------------------------

        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        title = QLabel("BLACKJACK")
        title.setObjectName("title")

        top_bar.addWidget(title)
        top_bar.addStretch()

        self.balance_labels = []

        for _ in range(2):
            label = QLabel("")
            label.setObjectName("balance")

            self.balance_labels.append(label)
            top_bar.addWidget(label)

        top_bar.addSpacing(6)

        self.menu_button = QPushButton("MENU")
        self.menu_button.setObjectName("menu_button")
        self.menu_button.setFocusPolicy(Qt.NoFocus)
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.clicked.connect(self.go_menu)

        top_bar.addWidget(self.menu_button)

        main_layout.addLayout(top_bar)

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        table = QFrame()
        table.setObjectName("table")

        table_layout = QVBoxLayout(table)
        table_layout.setContentsMargins(50, 35, 50, 35)
        table_layout.setSpacing(10)

        # -------------------------------------------------
        # DEALER
        # -------------------------------------------------

        dealer_title = QLabel("DEALER")
        dealer_title.setObjectName("section_title")
        dealer_title.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(dealer_title)

        self.dealer_value_label = QLabel("")
        self.dealer_value_label.setObjectName("hand_value")
        self.dealer_value_label.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(self.dealer_value_label)

        self.dealer_cards_layout = QHBoxLayout()
        self.dealer_cards_layout.setAlignment(Qt.AlignCenter)
        self.dealer_cards_layout.setSpacing(4)
        table_layout.addLayout(self.dealer_cards_layout)

        table_layout.addStretch()

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status_label = QLabel("PLACE YOUR BET")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(self.status_label)

        table_layout.addStretch()

        # -------------------------------------------------
        # PLAYERS
        # -------------------------------------------------

        self.seat_cards_layouts = []
        self.seat_titles = []
        self.seat_value_labels = []
        self.seat_bet_labels = []

        seats_row = QHBoxLayout()
        seats_row.setSpacing(30)

        for index, seat in enumerate(self.game.seats):
            column = QVBoxLayout()
            column.setSpacing(10)

            cards_layout = QHBoxLayout()
            cards_layout.setAlignment(Qt.AlignCenter)
            cards_layout.setSpacing(4)
            column.addLayout(cards_layout)

            seat_title = QLabel(seat.name)
            seat_title.setObjectName("section_title")
            seat_title.setAlignment(Qt.AlignCenter)
            column.addWidget(seat_title)

            value_label = QLabel("")
            value_label.setObjectName("hand_value")
            value_label.setAlignment(Qt.AlignCenter)
            column.addWidget(value_label)

            bet_label = QLabel("")
            bet_label.setObjectName("hand_value")
            bet_label.setAlignment(Qt.AlignCenter)
            column.addWidget(bet_label)

            self.seat_cards_layouts.append(cards_layout)
            self.seat_titles.append(seat_title)
            self.seat_value_labels.append(value_label)
            self.seat_bet_labels.append(bet_label)

            seats_row.addLayout(column, 1)

            if index == 0:
                divider = QFrame()
                divider.setObjectName("divider")
                seats_row.addWidget(divider)

        table_layout.addLayout(seats_row)

        main_layout.addWidget(table, stretch=1)

        # -------------------------------------------------
        # ACTION BAR
        # -------------------------------------------------

        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(40)

        self.hit_buttons = []
        self.stand_buttons = []

        for index in range(2):
            group = QHBoxLayout()
            group.setSpacing(12)

            hit_button = QPushButton("HIT")
            hit_button.setObjectName("hit_button")
            hit_button.setEnabled(False)
            hit_button.clicked.connect(
                lambda checked=False, i=index: self.hit(i)
            )

            stand_button = QPushButton("STAND")
            stand_button.setObjectName("stand_button")
            stand_button.setEnabled(False)
            stand_button.clicked.connect(
                lambda checked=False, i=index: self.stand(i)
            )

            self.hit_buttons.append(hit_button)
            self.stand_buttons.append(stand_button)

            group.addWidget(hit_button)
            group.addWidget(stand_button)

            bottom_bar.addLayout(group, 1)

        main_layout.addLayout(bottom_bar)

        self.setStyleSheet(STYLE)

    # =====================================================
    # BUTTONS
    # =====================================================

    def disable_buttons(self):
        for index in range(2):
            self.hit_buttons[index].setEnabled(False)
            self.stand_buttons[index].setEnabled(False)

    def update_buttons(self):
        """Sadece sırası gelen oyuncunun butonları açık olur."""
        game = self.game

        for index in range(2):
            mine = game.current == index

            self.hit_buttons[index].setEnabled(
                mine and game.can_hit
            )
            self.stand_buttons[index].setEnabled(
                mine and game.can_stand
            )

    # =====================================================
    # MENU
    # =====================================================

    def go_menu(self):
        if self._left:
            return

        self._left = True
        self.dealer_animation_started = False

        QTimer.singleShot(0, self.on_menu)

    # =====================================================
    # BETTING (her oyuncu sırayla bahis verir)
    # =====================================================

    def collect_bets(self):
        if self._left:
            return

        self.disable_buttons()

        if all(seat.balance <= 0 for seat in self.game.seats):
            self.set_active_seat(None)

            self.status_label.setText(
                "GAME OVER • NO BALANCE"
            )

            return

        self.set_active_seat(None)

        dialog = DualBetDialog(self.game.seats, self)

        code = dialog.exec()

        if code == MENU_CODE:
            self.go_menu()
            return

        if code != QDialog.Accepted:
            return

        bets = dialog.bets()

        if not bets:
            return

        self.start_new_round(bets)

    def finish_round_popup(self):
        if self._left:
            return

        self.disable_buttons()

        self.update_balances()

        self.collect_bets()

    def start_new_round(self, bets):
        success, result = self.game.start_round(bets)

        if not success:
            self.status_label.setText(result)
            return

        self.round_participants = sorted(bets)

        self.start_initial_deal_animation()

    # =====================================================
    # HIT / STAND
    # =====================================================

    def hit(self, index):
        if not self.game.can_hit or self.game.current != index:
            return

        success, result = self.game.hit()

        if not success:
            return

        self.disable_buttons()

        QTimer.singleShot(
            180,
            lambda i=index, r=result:
            self.finish_hit_animation(i, r),
        )

    def finish_hit_animation(self, index, result):
        self.update_balances()
        self.update_seat(index)

        seat = self.game.seats[index]

        if result == "BUST":
            self.status_label.setText(
                f"{seat.name} BUST • {seat.hand.value}"
            )

            QTimer.singleShot(1000, self.after_turn)

            return

        if result == "21":
            self.status_label.setText(
                f"{seat.name} • 21!"
            )

            QTimer.singleShot(500, self.after_turn)

            return

        self.update_buttons()

        self.status_label.setText(self.turn_text())

    def stand(self, index):
        if not self.game.can_stand or self.game.current != index:
            return

        success, _ = self.game.stand()

        if not success:
            return

        self.disable_buttons()

        self.after_turn()

    def after_turn(self):
        """Bir oyuncunun sırası bitti: sıradaki oyuncu / dealer / el sonu."""
        if self._left:
            return

        self.update_balances()

        game = self.game

        # Herkes battı -> dealer oynamaz
        if game.round_finished:
            self.set_active_seat(None)

            self.status_label.setText(self.results_text())

            QTimer.singleShot(1000, self.finish_round_popup)

        elif game.dealer_turn:
            self.set_active_seat(None)

            self.status_label.setText("DEALER TURN...")

            self.start_dealer_animation(reveal_delay=500)

        else:
            self.begin_turn()

    def begin_turn(self):
        game = self.game

        self.set_active_seat(game.current)

        self.update_buttons()

        self.status_label.setText(self.turn_text())

    def turn_text(self):
        seat = self.game.seats[self.game.current]

        return f"{seat.name} TURN  •  {seat.hand.value}"

    def results_text(self):
        parts = []

        for index, seat in enumerate(self.game.seats):
            if seat.in_round:
                parts.append(
                    f"P{index + 1}: {seat.last_result}"
                )

        return "   |   ".join(parts)

    # =====================================================
    # INITIAL DEAL ANIMATION
    # =====================================================

    def start_initial_deal_animation(self):
        self.deal_animation_index = 0
        self.deal_sequence = []

        for pass_no in (0, 1):
            for index in self.round_participants:
                self.deal_sequence.append(
                    ("player", index, pass_no)
                )

            self.deal_sequence.append(
                ("dealer", None, pass_no)
            )

        for index, seat in enumerate(self.game.seats):
            self.clear_layout(self.seat_cards_layouts[index])
            self.seat_value_labels[index].setText("")

            if seat.in_round:
                self.seat_bet_labels[index].setText(
                    f"BET ${seat.bet:,}"
                )
            else:
                self.seat_bet_labels[index].setText("")

        self.clear_layout(self.dealer_cards_layout)
        self.dealer_value_label.setText("")

        self.set_active_seat(None)

        self.status_label.setText("DEALING...")

        self.disable_buttons()

        QTimer.singleShot(250, self.animate_initial_deal)

    def animate_initial_deal(self):
        if self.deal_animation_index >= len(self.deal_sequence):
            self.finish_initial_deal_animation()
            return

        kind, index, card_no = self.deal_sequence[
            self.deal_animation_index
        ]

        if kind == "player":
            seat = self.game.seats[index]

            card = seat.hand.cards[card_no]

            self.seat_cards_layouts[index].addWidget(
                CardLabel(card.image_name)
            )

            self.seat_value_labels[index].setText(
                str(
                    calculate_hand_value(
                        seat.hand.cards[:card_no + 1]
                    )
                )
            )

        else:
            card = self.game.dealer_hand.cards[card_no]

            if card_no == 1:
                label = CardLabel("back")
            else:
                label = CardLabel(card.image_name)

            self.dealer_cards_layout.addWidget(label)

            if card_no == 0:
                self.dealer_value_label.setText(
                    f"{card.value} + ?"
                )

        self.deal_animation_index += 1

        QTimer.singleShot(320, self.animate_initial_deal)

    def finish_initial_deal_animation(self):
        self.update_balances()

        for index in self.round_participants:
            self.update_seat(index)

        # -------------------------------------------------
        # NATURAL BLACKJACK (dealer'da ya da herkeste)
        # -------------------------------------------------

        if self.game.round_finished:
            self.update_dealer(reveal=True)

            self.status_label.setText(self.results_text())

            QTimer.singleShot(1200, self.finish_round_popup)

            return

        self.begin_turn()

    # =====================================================
    # DEALER ANIMATION
    # =====================================================

    def start_dealer_animation(self, reveal_delay=500):
        self.dealer_animation_index = 0
        self.dealer_animation_started = True

        self.clear_layout(self.dealer_cards_layout)

        self.dealer_value_label.setText("")

        QTimer.singleShot(
            reveal_delay,
            self.animate_dealer_reveal,
        )

    def animate_dealer_reveal(self):
        if not self.dealer_animation_started:
            return

        cards = self.game.dealer_hand.cards

        if not cards:
            self.end_dealer_animation()
            return

        self.dealer_cards_layout.addWidget(
            CardLabel(cards[0].image_name)
        )

        self.dealer_animation_index = 1

        self.dealer_value_label.setText(
            str(calculate_hand_value(cards[:1]))
        )

        QTimer.singleShot(500, self.animate_dealer_hole_card)

    def animate_dealer_hole_card(self):
        if not self.dealer_animation_started:
            return

        cards = self.game.dealer_hand.cards

        if len(cards) < 2:
            self.request_dealer_step()
            return

        self.dealer_cards_layout.addWidget(
            CardLabel(cards[1].image_name)
        )

        self.dealer_animation_index = 2

        self.dealer_value_label.setText(
            str(calculate_hand_value(cards[:2]))
        )

        QTimer.singleShot(500, self.request_dealer_step)

    def request_dealer_step(self):
        if not self.dealer_animation_started:
            return

        if self.game.dealer_finished:
            self.end_dealer_animation()
            return

        success, result = self.game.dealer_step()

        if not success:
            self.dealer_animation_started = False

            self.status_label.setText(result)

            return

        self.animate_new_dealer_card()

    def animate_new_dealer_card(self):
        if not self.dealer_animation_started:
            return

        cards = self.game.dealer_hand.cards

        index = self.dealer_animation_index

        if index >= len(cards):
            if self.game.dealer_finished:
                self.end_dealer_animation()
            else:
                QTimer.singleShot(500, self.request_dealer_step)

            return

        self.dealer_cards_layout.addWidget(
            CardLabel(cards[index].image_name)
        )

        self.dealer_animation_index += 1

        self.dealer_value_label.setText(
            str(
                calculate_hand_value(
                    cards[:self.dealer_animation_index]
                )
            )
        )

        if self.game.dealer_finished:
            QTimer.singleShot(500, self.end_dealer_animation)
            return

        QTimer.singleShot(500, self.request_dealer_step)

    def end_dealer_animation(self):
        if not self.dealer_animation_started:
            return

        self.dealer_animation_started = False

        self.dealer_value_label.setText(
            str(self.game.dealer_hand.value)
        )

        self.update_balances()

        for index in self.round_participants:
            self.update_seat(index)

        self.status_label.setText(self.results_text())

        QTimer.singleShot(1200, self.finish_round_popup)

    # =====================================================
    # UI UPDATE
    # =====================================================

    def update_balances(self):
        for index, seat in enumerate(self.game.seats):
            self.balance_labels[index].setText(
                f"{seat.name}   ${seat.balance:,}"
            )

    def update_seat(self, index):
        seat = self.game.seats[index]

        self.clear_layout(self.seat_cards_layouts[index])

        for card in seat.hand.cards:
            self.seat_cards_layouts[index].addWidget(
                CardLabel(card.image_name)
            )

        if seat.hand.cards:
            text = str(seat.hand.value)

            if seat.hand.blackjack:
                text += "  •  BLACKJACK"

            elif seat.hand.bust:
                text += "  •  BUST"

            self.seat_value_labels[index].setText(text)

        elif seat.state == "out" and seat.balance <= 0:
            self.seat_value_labels[index].setText(
                "OUT OF CHIPS"
            )

        else:
            self.seat_value_labels[index].setText("")

    def update_dealer(self, reveal=False):
        self.clear_layout(self.dealer_cards_layout)

        cards = self.game.dealer_hand.cards

        for index, card in enumerate(cards):
            if index == 1 and not reveal:
                label = CardLabel("back")
            else:
                label = CardLabel(card.image_name)

            self.dealer_cards_layout.addWidget(label)

        if reveal:
            self.dealer_value_label.setText(
                str(self.game.dealer_hand.value)
            )

        elif cards:
            self.dealer_value_label.setText(
                f"{cards[0].value} + ?"
            )

        else:
            self.dealer_value_label.setText("")

    def set_active_seat(self, active_index):
        for index in range(2):
            active = index == active_index

            for widget in (
                self.seat_titles[index],
                self.balance_labels[index],
            ):
                widget.setProperty("active", active)
                widget.style().unpolish(widget)
                widget.style().polish(widget)

    # =====================================================
    # HELPERS
    # =====================================================

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

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
