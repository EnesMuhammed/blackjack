# ♠️ BLACKJACK

A desktop Blackjack game built with **Python** and **PySide6**, featuring both **single-player and two-player game modes**, betting, balance management, animated dealer turns, and a custom graphical interface.

The project separates the **game logic** from the **GUI**, making the core Blackjack mechanics reusable across different game modes.

---

## 🎮 Features

* **Single-player mode** against the dealer
* **Two-player mode** on the same computer
* Betting and balance system
* Standard 52-card deck
* Automatic deck shuffling
* Correct Ace handling as `1` or `11`
* Natural Blackjack detection
* **3:2 Blackjack payout**
* Dealer stands on **17 or higher**
* Hit / Stand actions
* Bust detection
* Push / tie handling
* Dealer turn animation
* Custom card graphics
* Keyboard shortcuts
* Fullscreen support
* Game-over handling when balance reaches zero
* Separate game logic and interface layers

---

## 🖥️ Game Modes

### 1 Player

Play against the dealer using a virtual starting balance.

The player can:

* Place a bet
* Hit to draw another card
* Stand to end their turn
* Win or lose based on the final hand values
* Receive a 3:2 payout for a natural Blackjack

The dealer automatically plays according to the game rules.

### 2 Players

Two players can play on the same computer.

Each player has:

* An independent balance
* Their own bet
* Their own hand
* An individual turn
* An independent round result

The dealer only plays after all active players have completed their turns.

---

## 🃏 Blackjack Rules

The game implements the following rules:

| Rule              | Implementation                    |
| ----------------- | --------------------------------- |
| Card values       | Standard Blackjack values         |
| Face cards        | `J`, `Q`, `K` = 10                |
| Ace               | 1 or 11 depending on hand value   |
| Natural Blackjack | 2 cards totaling 21               |
| Blackjack payout  | 3:2                               |
| Dealer            | Stands on 17+                     |
| Bust              | Hand value above 21               |
| Push              | Equal player and dealer values    |
| Deck              | Standard 52-card deck             |
| Shuffle           | Deck is reshuffled for each round |

The core game engine handles Ace conversion dynamically so hands such as `A + 9 + A` are evaluated correctly rather than blindly treating every Ace as 11.

---

## 🏗️ Architecture

The project is divided into several layers rather than putting the entire game inside the UI.

```text
blackjack/
│
├── main.py
├── menu.py
├── blackjack.py
│
├── game.py
├── game2p.py
│
├── single_player.py
├── two_player.py
│
├── dialogs.py
│
├── LICENSE
└── README.md
```

### `game.py`

Contains the core single-player Blackjack engine.

It defines:

* `Card`
* `Deck`
* `Hand`
* `BlackjackGame`

The game engine manages cards, bets, balances, player actions, dealer behavior, round states, payouts, and results independently from the graphical interface.

### `game2p.py`

Contains the two-player game engine.

The two-player implementation reuses the existing `Deck` and `Hand` classes instead of duplicating the underlying card logic. Each player is represented by a `Seat` object with its own balance, bet, hand, state, and result information.

### `blackjack.py`

Contains the main graphical Blackjack window and UI components.

It handles:

* Card rendering
* Player/dealer displays
* Betting interface
* Game controls
* Balance display
* Game status
* Dealer animation
* Qt event handling

Card images are loaded dynamically from the project's card assets.

### `single_player.py`

Provides the single-player window and connects the core game engine with the main application menu. It also handles the betting dialog and menu navigation.

### `two_player.py`

Provides the two-player graphical interface and connects it to `TwoPlayerBlackjackGame`.

The interface visually tracks the active player and separates the two players' balances, hands, and actions.

### `menu.py`

Contains the main menu and game-mode selection screen.

It also provides keyboard shortcuts for selecting game modes and toggling fullscreen mode.

### `dialogs.py`

Contains reusable dialogs used throughout the application, including betting and two-player betting interfaces.

---

## ⚙️ Technical Details

### Game State Management

The game engine uses explicit state flags to control the flow of a round.

For example:

```text
Player Turn
    │
    ├── Hit ──→ Continue
    │
    ├── Hit ──→ Bust ──→ Round End
    │
    └── Stand
          │
          ▼
     Dealer Turn
          │
          ├── Dealer < 17 → Draw
          │
          └── Dealer ≥ 17 → Evaluate Round
```

This keeps player actions, dealer actions, and round completion separate instead of allowing the UI to directly manipulate game state.

### Dealer Animation

The dealer does not have to finish its entire turn instantly.

The game engine exposes a `dealer_step()` operation which allows the GUI to request individual dealer actions. `QTimer` can then be used by the interface to reveal cards sequentially, creating a natural dealer animation.

### Reusable Game Logic

The two-player implementation reuses the same `Deck` and `Hand` classes from the single-player engine.

This avoids duplicating fundamental card-handling logic and keeps both game modes consistent.

---

## 🛠️ Tech Stack

* **Python**
* **PySide6 / Qt**
* Object-Oriented Programming
* Event-driven GUI programming
* State-based game logic

---

## 🚀 Installation

### Requirements

* Python 3.10+
* PySide6

Install PySide6:

```bash
pip install PySide6
```

Clone the repository:

```bash
git clone https://github.com/EnesMuhammed/blackjack.git
cd blackjack
```

Run the application:

```bash
python main.py
```

---

## 🎯 Project Goals

This project was built to practice and demonstrate:

* Object-oriented programming in Python
* Designing reusable game logic
* GUI development with PySide6
* Event-driven programming
* Managing complex application state
* Implementing game rules accurately
* Separating business logic from presentation
* Building a complete desktop application from scratch

---

## 📄 License

This project is licensed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for details.

---

## 👨‍💻 Author

**Enes Muhammed**

GitHub: [@EnesMuhammed](https://github.com/EnesMuhammed)
