from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MenuWindow(QMainWindow):
    def __init__(self, on_single, on_two, on_quit):
        super().__init__()

        self.on_single = on_single
        self.on_two = on_two
        self.on_quit = on_quit

        self.setWindowTitle("Blackjack")
        self.setMinimumSize(1100, 700)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(40, 30, 40, 30)

        outer.addStretch()

        row = QHBoxLayout()
        row.addStretch()

        panel = QFrame()
        panel.setObjectName("table")
        panel.setFixedWidth(620)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 45, 50, 45)
        layout.setSpacing(16)

        title = QLabel("BLACKJACK")
        title.setObjectName("menu_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("SELECT GAME MODE")
        subtitle.setObjectName("section_title")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(14)

        one = QPushButton("1 PLAYER")
        one.setObjectName("mode_button")
        one.setCursor(Qt.PointingHandCursor)
        one.clicked.connect(
            lambda checked=False: self.on_single()
        )
        layout.addWidget(one)

        two = QPushButton("2 PLAYERS")
        two.setObjectName("mode_button")
        two.setCursor(Qt.PointingHandCursor)
        two.clicked.connect(
            lambda checked=False: self.on_two()
        )
        layout.addWidget(two)

        layout.addSpacing(6)

        quit_button = QPushButton("QUIT")
        quit_button.setObjectName("quit_button")
        quit_button.setCursor(Qt.PointingHandCursor)
        quit_button.clicked.connect(
            lambda checked=False: self.on_quit()
        )
        layout.addWidget(quit_button)

        hint = QLabel("1 / 2  •  SELECT      F11  •  FULLSCREEN")
        hint.setObjectName("hand_value")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        row.addWidget(panel)
        row.addStretch()

        outer.addLayout(row)
        outer.addStretch()

        self.setStyleSheet(
            """
            QMainWindow {
                background: #07130f;
            }

            QWidget#central {
                background: #07130f;
            }

            QFrame#table {
                background: #0b4a35;

                border: 1px solid #146547;
                border-radius: 30px;
            }

            QLabel#menu_title {
                color: white;
                font-size: 48px;
                font-weight: 800;
                letter-spacing: 4px;
            }

            QLabel#section_title {
                color: #9bbcaf;

                font-size: 15px;
                font-weight: 700;

                letter-spacing: 2px;
            }

            QLabel#hand_value {
                color: #d8e9e1;

                font-size: 13px;
                font-weight: 600;
            }

            QPushButton {
                border: none;
                border-radius: 10px;

                padding: 12px 22px;

                font-size: 14px;
                font-weight: 800;
            }

            QPushButton#mode_button {
                min-height: 44px;

                color: #07130f;
                background: #d8b45a;

                font-size: 20px;
                font-weight: 900;
            }

            QPushButton#mode_button:hover {
                background: #e6c566;
            }

            QPushButton#quit_button {
                color: #c8ddd4;
                background: #172b23;

                border: 1px solid #345548;
            }

            QPushButton#quit_button:hover {
                background: #b83b4b;
                color: white;
                border: 1px solid #b83b4b;
            }
            """
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self.on_single()

        elif event.key() == Qt.Key_2:
            self.on_two()

        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        elif event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()

        else:
            super().keyPressEvent(event)
