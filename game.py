import random


# =========================================================
# CARD
# =========================================================

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    @property
    def value(self):
        if self.rank in ("J", "Q", "K"):
            return 10

        if self.rank == "A":
            return 11

        return int(self.rank)

    @property
    def image_name(self):
        return f"{self.rank}{self.suit}"


# =========================================================
# DECK
# =========================================================

class Deck:
    SUITS = ("S", "H", "D", "C")

    RANKS = (
        "A",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.cards = [
            Card(rank, suit)
            for suit in self.SUITS
            for rank in self.RANKS
        ]

        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.reset()

        return self.cards.pop()


# =========================================================
# HAND
# =========================================================

class Hand:
    def __init__(self, bet=0):
        self.cards = []
        self.bet = bet

    def add(self, card):
        self.cards.append(card)

    @property
    def value(self):
        total = sum(
            card.value
            for card in self.cards
        )

        aces = sum(
            1
            for card in self.cards
            if card.rank == "A"
        )

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    @property
    def blackjack(self):
        return (
            len(self.cards) == 2
            and self.value == 21
        )

    @property
    def bust(self):
        return self.value > 21


# =========================================================
# BLACKJACK GAME
# =========================================================

class BlackjackGame:
    def __init__(self, starting_balance=1000):
        self.balance = starting_balance

        self.deck = Deck()

        self.player_hand = Hand()
        self.dealer_hand = Hand()

        self.bet = 0

        self.active = False

        self.round_finished = False

        self.dealer_finished = False

        self.dealer_turn = False

        self.last_result = ""
        self.last_profit = 0

    # =====================================================
    # ROUND
    # =====================================================

    def start_round(self, bet):
        if self.active:
            return False, "ROUND_ACTIVE"

        if self.dealer_turn:
            return False, "ROUND_ACTIVE"

        if bet <= 0:
            return False, "INVALID_BET"

        if bet > self.balance:
            return False, "INSUFFICIENT_BALANCE"

        # Yeni deste
        self.deck.reset()

        self.bet = bet

        # Bahsi bakiyeden düş
        self.balance -= bet

        self.player_hand = Hand(bet)
        self.dealer_hand = Hand()

        self.active = False
        self.round_finished = False
        self.dealer_finished = False
        self.dealer_turn = False

        self.last_result = ""
        self.last_profit = 0

        # =================================================
        # INITIAL DEAL
        # =================================================

        # 1. Player
        self.player_hand.add(
            self.deck.draw()
        )

        # 2. Dealer
        self.dealer_hand.add(
            self.deck.draw()
        )

        # 3. Player
        self.player_hand.add(
            self.deck.draw()
        )

        # 4. Dealer
        self.dealer_hand.add(
            self.deck.draw()
        )

        player_blackjack = (
            self.player_hand.blackjack
        )

        dealer_blackjack = (
            self.dealer_hand.blackjack
        )

        # =================================================
        # NATURAL BLACKJACK
        # =================================================

        if player_blackjack or dealer_blackjack:
            self.round_finished = True
            self.dealer_finished = True
            self.dealer_turn = False

            # ---------------------------------------------
            # BOTH BLACKJACK
            # ---------------------------------------------

            if (
                player_blackjack
                and dealer_blackjack
            ):
                # Bahsi geri ver
                self.balance += self.bet

                self.last_result = (
                    "PUSH • BOTH BLACKJACK"
                )

                self.last_profit = 0

            # ---------------------------------------------
            # PLAYER BLACKJACK
            # ---------------------------------------------

            elif player_blackjack:
                # 3:2 payout
                payout = int(
                    self.bet * 2.5
                )

                self.balance += payout

                self.last_result = (
                    "BLACKJACK • YOU WIN"
                )

                self.last_profit = int(
                    self.bet * 1.5
                )

            # ---------------------------------------------
            # DEALER BLACKJACK
            # ---------------------------------------------

            else:
                self.last_result = (
                    "DEALER BLACKJACK"
                )

                self.last_profit = -self.bet

            return True, self.last_result

        # Normal oyun başlıyor
        self.active = True

        return True, "OK"

    # =====================================================
    # HIT
    # =====================================================

    def hit(self):
        if not self.active:
            return False, "NO_ACTIVE_GAME"

        if self.dealer_turn:
            return False, "NO_ACTIVE_GAME"

        # Oyuncuya bir kart
        self.player_hand.add(
            self.deck.draw()
        )

        # ---------------------------------------------
        # BUST
        # ---------------------------------------------

        if self.player_hand.bust:
            self.active = False
            self.round_finished = True
            self.dealer_finished = False
            self.dealer_turn = False

            self.last_result = (
                "BUST • YOU LOSE"
            )

            self.last_profit = -self.bet

            return True, "BUST"

        # ---------------------------------------------
        # EXACT 21
        # ---------------------------------------------

        if self.player_hand.value == 21:
            # Burada artık dealer_play() çağırmıyoruz.
            #
            # UI'nin dealer kartlarını tek tek
            # animasyonla çekebilmesi için dealer
            # turunu başlatıyoruz.

            self.active = False
            self.round_finished = False
            self.dealer_finished = False
            self.dealer_turn = True

            return True, "21"

        return True, "OK"

    # =====================================================
    # STAND
    # =====================================================

    def stand(self):
        if not self.active:
            return False, "NO_ACTIVE_GAME"

        # Oyuncunun turu bitti.
        self.active = False

        # Dealer artık sırayla kart çekecek.
        self.dealer_turn = True
        self.dealer_finished = False
        self.round_finished = False

        return True, "OK"

    # =====================================================
    # DEALER STEP
    # =====================================================

    def dealer_step(self):
        """
        Dealer'a tek bir kart çeker.

        UI bunu QTimer ile çağırarak
        kartların tek tek görünmesini sağlar.

        Returns:
            (True, "DRAW")       -> yeni kart çekildi
            (True, "FINISHED")   -> dealer turu bitti
            (False, error)       -> işlem yapılamıyor
        """

        if not self.dealer_turn:
            return False, "NO_DEALER_TURN"

        if self.dealer_finished:
            return True, "FINISHED"

        # Dealer 17 veya üzerindeyse
        # artık kart çekmez.
        if self.dealer_hand.value >= 17:
            self.dealer_finished = True
            self.dealer_turn = False

            self.finish_round()

            return True, "FINISHED"

        # Bir kart çek
        self.dealer_hand.add(
            self.deck.draw()
        )

        # Yeni karttan sonra bust olduysa
        if self.dealer_hand.bust:
            self.dealer_finished = True
            self.dealer_turn = False

            self.finish_round()

            return True, "FINISHED"

        # Yeni kart sonrası 17+ olduysa
        if self.dealer_hand.value >= 17:
            self.dealer_finished = True
            self.dealer_turn = False

            self.finish_round()

            return True, "FINISHED"

        # Daha kart gerekiyor
        return True, "DRAW"

    # =====================================================
    # DEALER PLAY
    # =====================================================

    def dealer_play(self):
        """
        Animasyonsuz kullanım için dealer'ı
        tamamen oynatır.

        Normal UI artık dealer_step()
        kullanabilir.
        """

        if not self.dealer_turn:
            return False, "NO_DEALER_TURN"

        while not self.dealer_finished:
            success, result = self.dealer_step()

            if not success:
                return False, result

            if result == "FINISHED":
                break

        return True, "OK"

    # =====================================================
    # FINISH ROUND
    # =====================================================

    def finish_round(self):
        player = self.player_hand.value
        dealer = self.dealer_hand.value

        # ---------------------------------------------
        # PLAYER BUST
        # ---------------------------------------------

        if self.player_hand.bust:
            self.last_result = (
                "BUST • YOU LOSE"
            )

            self.last_profit = -self.bet

        # ---------------------------------------------
        # DEALER BUST
        # ---------------------------------------------

        elif self.dealer_hand.bust:
            self.balance += (
                self.bet * 2
            )

            self.last_result = (
                "DEALER BUST • YOU WIN"
            )

            self.last_profit = self.bet

        # ---------------------------------------------
        # PLAYER WINS
        # ---------------------------------------------

        elif player > dealer:
            self.balance += (
                self.bet * 2
            )

            self.last_result = (
                "YOU WIN"
            )

            self.last_profit = self.bet

        # ---------------------------------------------
        # DEALER WINS
        # ---------------------------------------------

        elif player < dealer:
            self.last_result = (
                "DEALER WINS"
            )

            self.last_profit = -self.bet

        # ---------------------------------------------
        # PUSH
        # ---------------------------------------------

        else:
            self.balance += self.bet

            self.last_result = "PUSH"

            self.last_profit = 0

        self.active = False
        self.dealer_turn = False
        self.dealer_finished = True
        self.round_finished = True

    # =====================================================
    # STATE
    # =====================================================

    @property
    def can_hit(self):
        return (
            self.active
            and not self.dealer_turn
            and not self.round_finished
        )

    @property
    def can_stand(self):
        return (
            self.active
            and not self.dealer_turn
            and not self.round_finished
        )

    @property
    def can_dealer_play(self):
        return (
            self.dealer_turn
            and not self.dealer_finished
            and not self.round_finished
        )
