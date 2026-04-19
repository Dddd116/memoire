from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.db_postgres import DatabaseConnection


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soft Sensor - Connexion")
        self.resize(1200, 760)
        self.setMinimumSize(1000, 680)

        self.db = DatabaseConnection()

        self.colors = {
            "primary": "#0a0e27",
            "secondary": "#16213e",
            "tertiary": "#1e2a5e",
            "accent": "#00d4ff",
            "text": "#ffffff",
            "text_muted": "#b8c1d9"
        }

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors["primary"]};
                color: {self.colors["text"]};
                font-family: Arial;
            }}

            QFrame#mainCard {{
                background-color: {self.colors["secondary"]};
                border: none;
                border-radius: 34px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}

            QLabel#titleLabel {{
                color: {self.colors["accent"]};
                font-size: 52px;
                font-weight: bold;
            }}

            QLabel#subtitleLabel {{
                color: {self.colors["text_muted"]};
                font-size: 24px;
                font-weight: 500;
            }}

            QLabel#sectionTitle {{
                color: {self.colors["text"]};
                font-size: 24px;
                font-weight: bold;
            }}

            QLabel#smallInfo {{
                color: {self.colors["text_muted"]};
                font-size: 18px;
            }}

            QLineEdit {{
                background-color: {self.colors["tertiary"]};
                color: {self.colors["text"]};
                border: 1px solid rgba(0,212,255,0.35);
                border-radius: 20px;
                padding: 20px;
                font-size: 22px;
                min-height: 38px;
            }}

            QLineEdit:focus {{
                border: 1px solid {self.colors["accent"]};
            }}

            QPushButton#loginButton {{
                background-color: {self.colors["accent"]};
                color: black;
                border: none;
                border-radius: 20px;
                padding: 20px;
                font-size: 22px;
                font-weight: bold;
                min-height: 65px;
            }}

            QPushButton#loginButton:hover {{
                background-color: #4ce2ff;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("mainCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(90, 60, 90, 60)
        card_layout.setSpacing(24)

        icon_label = QLabel("🏭")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Arial", 72))

        title = QLabel("Connexion")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Accédez à votre espace de supervision")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)

        user_label = QLabel("Utilisateur")
        user_label.setObjectName("sectionTitle")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Entrer le nom d'utilisateur")

        password_label = QLabel("Mot de passe")
        password_label.setObjectName("sectionTitle")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Entrer le mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.authenticate)

        btn = QPushButton("CONNEXION")
        btn.setObjectName("loginButton")
        btn.clicked.connect(self.authenticate)

        info = QLabel("Entrer vos identifiants")
        info.setObjectName("smallInfo")
        info.setAlignment(Qt.AlignCenter)

        card_layout.addStretch()
        card_layout.addWidget(icon_label)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(18)
        card_layout.addWidget(user_label)
        card_layout.addWidget(self.username)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password)
        card_layout.addSpacing(18)
        card_layout.addWidget(btn)
        card_layout.addWidget(info)
        card_layout.addStretch()

        main_layout.addWidget(card)

        self.main_window = None

    def authenticate(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Champs vides", "Veuillez remplir tous les champs")
            return

        if self.db.verify_user(username, password):
            from ui.main_window import MainWindow
            self.main_window = MainWindow(current_user=username)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect")