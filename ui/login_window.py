from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QCheckBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.db_postgres import DatabaseConnection


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soft Sensor — Connexion")
        self.resize(1200, 760)
        self.setMinimumSize(1000, 680)

        self.db = DatabaseConnection()
        self.password_visible = False

        self.colors = {
            "primary":      "#0a0e27",
            "secondary":    "#16213e",
            "tertiary":     "#1e2a5e",
            "accent":       "#00d4ff",
            "accent2":      "#0099bb",
            "error":        "#ff5252",
            "text":         "#ffffff",
            "text_muted":   "#b8c1d9",
            "border":       "rgba(0,212,255,0.30)",
            "border_focus": "#00d4ff",
        }

        self._apply_stylesheet()
        self._build_ui()

    # ─────────────────────────────────────────
    #  Stylesheet
    # ─────────────────────────────────────────
    def _apply_stylesheet(self):
        c = self.colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['primary']};
                color: {c['text']};
                font-family: 'Segoe UI', sans-serif;
            }}

            QFrame#mainCard {{
                background-color: {c['secondary']};
                border-radius: 28px;
            }}

            QLabel {{ background: transparent; border: none; }}

            QLabel#titleLabel {{
                color: {c['accent']};
                font-size: 44px;
                font-weight: 800;
                letter-spacing: 1px;
            }}

            QLabel#subtitleLabel {{
                color: {c['text_muted']};
                font-size: 18px;
            }}

            QLabel#fieldLabel {{
                color: {c['text']};
                font-size: 15px;
                font-weight: 600;
            }}

            QLabel#errorLabel {{
                color: {c['error']};
                font-size: 14px;
                font-weight: 600;
            }}

            QLineEdit {{
                background-color: {c['tertiary']};
                color: {c['text']};
                border: 1.5px solid {c['border']};
                border-radius: 14px;
                padding: 14px 50px 14px 16px;
                font-size: 16px;
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {c['border_focus']};
                background-color: #253070;
            }}

            QPushButton#loginButton {{
                background-color: {c['accent']};
                color: #000000;
                border: none;
                border-radius: 14px;
                padding: 14px;
                font-size: 17px;
                font-weight: 700;
                min-height: 20px;
            }}
            QPushButton#loginButton:hover  {{ background-color: #4ce2ff; }}
            QPushButton#loginButton:pressed {{ background-color: {c['accent2']}; }}

            QPushButton#eyeButton {{
                background: transparent;
                border: none;
                color: {c['text_muted']};
                font-size: 18px;
                padding: 0px;
            }}
            QPushButton#eyeButton:hover {{ color: {c['accent']}; }}

            QCheckBox {{
                color: {c['text_muted']};
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border-radius: 5px;
                border: 1.5px solid {c['border']};
                background: {c['tertiary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {c['accent']};
                border-color: {c['accent']};
            }}
        """)

    # ─────────────────────────────────────────
    #  UI
    # ─────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)

        card = QFrame()
        card.setObjectName("mainCard")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(100, 56, 100, 56)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignCenter)

        # ── Icône ──
        icon_lbl = QLabel("🏭")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 60))
        lay.addWidget(icon_lbl)
        lay.addSpacing(10)

        # ── Titre ──
        title = QLabel("Connexion")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)
        lay.addSpacing(6)

        # ── Sous-titre ──
        subtitle = QLabel("Accédez à votre espace de supervision")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        lay.addWidget(subtitle)
        lay.addSpacing(32)

        # ── Champ nom d'utilisateur ──
        user_label = QLabel("👤  Nom d'utilisateur")
        user_label.setObjectName("fieldLabel")
        lay.addWidget(user_label)
        lay.addSpacing(6)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lay.addWidget(self.username)
        lay.addSpacing(18)

        # ── Champ mot de passe ──
        pwd_label = QLabel("🔒  Mot de passe")
        pwd_label.setObjectName("fieldLabel")
        lay.addWidget(pwd_label)
        lay.addSpacing(6)

        # Conteneur mot de passe + bouton œil
        pwd_container = QWidget()
        pwd_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pwd_h = QHBoxLayout(pwd_container)
        pwd_h.setContentsMargins(0, 0, 0, 0)
        pwd_h.setSpacing(0)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Entrez votre mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.authenticate)
        self.password.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setObjectName("eyeButton")
        self.eye_btn.setFixedSize(38, 38)
        self.eye_btn.setCursor(Qt.PointingHandCursor)
        self.eye_btn.clicked.connect(self._toggle_password)

        pwd_h.addWidget(self.password)

        # On place le bouton œil en overlay dans le champ
        self.eye_btn.setParent(pwd_container)
        self._pwd_container = pwd_container

        lay.addWidget(pwd_container)
        lay.addSpacing(6)

        # ── Message d'erreur ──
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        lay.addWidget(self.error_label)
        lay.addSpacing(10)

        # ── Se souvenir + mot de passe oublié ──
        extras = QHBoxLayout()
        self.remember_cb = QCheckBox("Se souvenir de moi")
        self.remember_cb.setCursor(Qt.PointingHandCursor)

        forgot = QLabel('<a href="#" style="color:#00d4ff;text-decoration:underline;">Mot de passe oublié ?</a>')
        forgot.setTextFormat(Qt.RichText)
        forgot.setTextInteractionFlags(Qt.TextBrowserInteraction)
        forgot.setCursor(Qt.PointingHandCursor)
        forgot.linkActivated.connect(self._forgot_password)

        extras.addWidget(self.remember_cb)
        extras.addStretch()
        extras.addWidget(forgot)
        lay.addLayout(extras)
        lay.addSpacing(24)

        # ── Bouton Se connecter ──
        self.login_btn = QPushButton("✔  Se connecter")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.authenticate)
        lay.addWidget(self.login_btn)

        root.addWidget(card)
        self.main_window = None

    # ─────────────────────────────────────────
    #  Repositionner le bouton œil
    # ─────────────────────────────────────────
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._place_eye()

    def showEvent(self, event):
        super().showEvent(event)
        self._place_eye()

    def _place_eye(self):
        if hasattr(self, '_pwd_container') and hasattr(self, 'eye_btn'):
            c = self._pwd_container
            bw = self.eye_btn.width()
            bh = self.eye_btn.height()
            self.eye_btn.move(c.width() - bw - 8, (c.height() - bh) // 2)
            self.eye_btn.raise_()

    # ─────────────────────────────────────────
    #  Actions
    # ─────────────────────────────────────────
    def _toggle_password(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("🙈")
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("👁")

    def _forgot_password(self, _=None):
        QMessageBox.information(
            self, "Mot de passe oublié",
            "Veuillez contacter votre administrateur système\n"
            "pour réinitialiser votre mot de passe."
        )

    def _show_error(self, msg: str):
        self.error_label.setText(f"⚠️  {msg}")
        self.error_label.show()

    def _clear_error(self):
        self.error_label.hide()
        self.error_label.setText("")

    def authenticate(self):
        self._clear_error()
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            self._show_error("Veuillez remplir tous les champs.")
            return

        if self.db.verify_user(username, password):
            from ui.main_window import MainWindow
            self.main_window = MainWindow(current_user=username)
            self.main_window.show()
            self.close()
        else:
            self._show_error("Identifiants incorrects. Veuillez réessayer.")
            self.password.clear()
            self.password.setFocus()