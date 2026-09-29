"""
2 oyunculu blackjack mantığı.

game.py'ye DOKUNMAZ; sadece oradaki Deck ve Hand sınıflarını kullanır.
Kurallar tek oyunculu ile birebir aynıdır:
- Dealer 17 ve üstünde durur
- Blackjack 3:2 öder
- Bahis başlangıçta bakiyeden düşülür
"""

from game import Deck, Hand


class Seat:
    """Bir oyuncunun masadaki durumu."""

    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.hand = Hand()
        self.bet = 0

        # out      -> bu elde oynamıyor
        # playing  -> sırasını bekliyor / oynuyor
        # stood    -> durdu (ya da 21 yaptı), dealer bekleniyor
        # bust     -> battı
        # done     -> el sonuçlandı
        self.state = "out"

        self.last_result = ""
        self.last_profit = 0

    @property
    def in_round(self):
        return self.state != "out"


class TwoPlayerBlackjackGame:
    def __init__(self, starting_balance=1000):
        self.deck = Deck()

        self.seats = [
            Seat("PLAYER 1", starting_balance),
            Seat("PLAYER 2", starting_balance),
        ]

        self.dealer_hand = Hand()

        self.current = None

        self.round_active = False
        self.round_finished = False
        self.dealer_turn = False
        self.dealer_finished = False

    # =====================================================
    # ROUND
    # =====================================================

    def start_round(self, bets):
        """
        bets: {seat_index: amount}
        Bakiyesi biten oyuncu bahis vermez, o el oturur.
        """
        if self.round_active:
            return False, "ROUND_ACTIVE"

        if not bets:
            return False, "INVALID_BET"

        for index, amount in bets.items():
            if index not in (0, 1):
                return False, "INVALID_BET"

            if amount <= 0:
                return False, "INVALID_BET"

            if amount > self.seats[index].balance:
                return False, "INSUFFICIENT_BALANCE"

        self.deck.reset()

        self.dealer_hand = Hand()
        self.current = None

        self.round_active = True
        self.round_finished = False
        self.dealer_turn = False
        self.dealer_finished = False

        for index, seat in enumerate(self.seats):
            seat.hand = Hand()
            seat.bet = 0
            seat.state = "out"

            if index in bets:
                seat.bet = bets[index]
                seat.balance -= seat.bet
                seat.hand = Hand(seat.bet)
                seat.state = "playing"
                seat.last_result = ""
                seat.last_profit = 0

        participants = sorted(bets)

        # Dağıtım: oyuncular sırayla, dealer, tekrar oyuncular, dealer
        for _ in range(2):
            for index in participants:
                self.seats[index].hand.add(self.deck.draw())

            self.dealer_hand.add(self.deck.draw())

        dealer_blackjack = self.dealer_hand.blackjack

        # -------------------------------------------------
        # NATURAL BLACKJACK
        # -------------------------------------------------

        if dealer_blackjack:
            for index in participants:
                seat = self.seats[index]

                if seat.hand.blackjack:
                    seat.balance += seat.bet
                    seat.last_result = "PUSH • BOTH BLACKJACK"
                    seat.last_profit = 0
                else:
                    seat.last_result = "DEALER BLACKJACK"
                    seat.last_profit = -seat.bet

                seat.state = "done"

            self._finish_all()
            return True, "OK"

        for index in participants:
            seat = self.seats[index]

            if seat.hand.blackjack:
                seat.balance += int(seat.bet * 2.5)
                seat.last_result = "BLACKJACK • YOU WIN"
                seat.last_profit = int(seat.bet * 1.5)
                seat.state = "done"

        first = self._next_playing(-1)

        if first is None:
            self._finish_all()
        else:
            self.current = first

        return True, "OK"

    # =====================================================
    # PLAYER ACTIONS
    # =====================================================

    def hit(self):
        if not self.can_hit:
            return False, "NO_ACTIVE_GAME"

        seat = self.seats[self.current]

        seat.hand.add(self.deck.draw())

        if seat.hand.bust:
            seat.state = "bust"
            seat.last_result = "BUST • YOU LOSE"
            seat.last_profit = -seat.bet

            self._advance()

            return True, "BUST"

        if seat.hand.value == 21:
            seat.state = "stood"

            self._advance()

            return True, "21"

        return True, "OK"

    def stand(self):
        if not self.can_stand:
            return False, "NO_ACTIVE_GAME"

        self.seats[self.current].state = "stood"

        self._advance()

        return True, "OK"

    # =====================================================
    # TURN FLOW
    # =====================================================

    def _next_playing(self, after):
        for index in range(after + 1, len(self.seats)):
            if self.seats[index].state == "playing":
                return index

        return None

    def _advance(self):
        nxt = self._next_playing(self.current)

        if nxt is not None:
            self.current = nxt
            return

        self.current = None

        # Dealer'ın oynaması gereken en az bir el var mı?
        if any(seat.state == "stood" for seat in self.seats):
            self.dealer_turn = True
            self.dealer_finished = False
        else:
            # Herkes battı -> dealer oynamaz
            self._finish_all()

    def _finish_all(self):
        self.current = None
        self.round_active = False
        self.round_finished = True
        self.dealer_turn = False
        self.dealer_finished = True

    # =====================================================
    # DEALER
    # =====================================================

    def dealer_step(self):
        if not self.dealer_turn:
            return False, "NO_DEALER_TURN"

        if self.dealer_finished:
            return True, "FINISHED"

        if self.dealer_hand.value >= 17:
            self._settle()
            return True, "FINISHED"

        self.dealer_hand.add(self.deck.draw())

        if self.dealer_hand.bust or self.dealer_hand.value >= 17:
            self._settle()
            return True, "FINISHED"

        return True, "DRAW"

    def _settle(self):
        dealer = self.dealer_hand.value

        for seat in self.seats:
            if seat.state != "stood":
                continue

            player = seat.hand.value

            if self.dealer_hand.bust:
                seat.balance += seat.bet * 2
                seat.last_result = "DEALER BUST • YOU WIN"
                seat.last_profit = seat.bet

            elif player > dealer:
                seat.balance += seat.bet * 2
                seat.last_result = "YOU WIN"
                seat.last_profit = seat.bet

            elif player < dealer:
                seat.last_result = "DEALER WINS"
                seat.last_profit = -seat.bet

            else:
                seat.balance += seat.bet
                seat.last_result = "PUSH"
                seat.last_profit = 0

            seat.state = "done"

        self._finish_all()

    # =====================================================
    # STATE
    # =====================================================

    @property
    def can_hit(self):
        return (
            self.round_active
            and self.current is not None
            and not self.dealer_turn
            and not self.round_finished
        )

    @property
    def can_stand(self):
        return self.can_hit
