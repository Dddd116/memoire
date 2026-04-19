from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QFrame, QLabel
)

from core.sensor_database import SensorDatabase
from ui.pages.dashboard_page import DashboardPage
from ui.pages.physical_page import PhysicalPage
from ui.pages.soft_page import SoftPage
from ui.pages.trends_page import TrendsPage
from ui.pages.alarms_page import AlarmsPage
from ui.pages.reports_page import ReportsPage


class MainWindow(QMainWindow):
    def __init__(self, current_user="admin"):
        super().__init__()

        self.current_user = current_user
        self.db = SensorDatabase()

        self.colors = {
            "primary": "#0a0e27",
            "secondary": "#131b3c",
            "tertiary": "#1e2a5e",
            "card_bg": "#16213e",
            "accent": "#00d4ff",
            "text": "#ffffff",
            "text_muted": "#8892b0"
        }

        self.setWindowTitle("Soft sensor")
        self.resize(1280, 820)
        self.setMinimumSize(1100, 700)

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {self.colors["primary"]};
                color: {self.colors["text"]};
                font-family: Arial;
                font-size: 16px;
            }}

            QFrame#header {{
                background-color: {self.colors["secondary"]};
                border: none;
                border-radius: 20px;
            }}

            QFrame#sidebar {{
                background-color: {self.colors["secondary"]};
                border: none;
                border-radius: 18px;
            }}

            QFrame#contentFrame {{
                background-color: {self.colors["card_bg"]};
                border: none;
                border-radius: 20px;
            }}

            QLabel#appTitle {{
                color: {self.colors["accent"]};
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}

            QLabel#userLabel {{
                color: {self.colors["text"]};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}

            QLabel#menuTitle {{
                color: {self.colors["accent"]};
                font-size: 22px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding-bottom: 8px;
            }}

            QPushButton#menuButton {{
                background-color: {self.colors["tertiary"]};
                color: {self.colors["text"]};
                border: none;
                border-radius: 14px;
                padding: 14px 16px;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }}

            QPushButton#menuButton:hover {{
                background-color: {self.colors["accent"]};
                color: black;
            }}

            QPushButton#logoutButton {{
                background-color: {self.colors["accent"]};
                color: black;
                border: none;
                border-radius: 14px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: bold;
            }}

            QPushButton#logoutButton:hover {{
                background-color: #5be5ff;
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(14)

        self.header = self.build_header()
        root_layout.addWidget(self.header)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(14)

        self.sidebar = self.build_sidebar()
        body_layout.addWidget(self.sidebar)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")

        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(14, 14, 14, 14)

        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)

        body_layout.addWidget(self.content_frame, 1)
        root_layout.addLayout(body_layout)

        self.pages = {
            "dashboard": DashboardPage(self),
            "physical": PhysicalPage(self),
            "soft": SoftPage(self),
            "trends": TrendsPage(self),
            "alarms": AlarmsPage(self),
            "reports": ReportsPage(self),
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.show_page("dashboard")

    def build_header(self):
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(85)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(22, 14, 22, 14)
        layout.setSpacing(12)

        title = QLabel("Soft sensor")
        title.setObjectName("appTitle")

        user_label = QLabel(self.current_user)
        user_label.setObjectName("userLabel")
        user_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        logout_button = QPushButton("Déconnexion")
        logout_button.setObjectName("logoutButton")
        logout_button.clicked.connect(self.close)

        right_box = QHBoxLayout()
        right_box.setSpacing(10)
        right_box.addWidget(user_label)
        right_box.addWidget(logout_button)

        layout.addWidget(title)
        layout.addStretch()
        layout.addLayout(right_box)

        return header

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        menu_title = QLabel("MENU PRINCIPAL")
        menu_title.setObjectName("menuTitle")
        menu_title.setAlignment(Qt.AlignCenter)

        btn_dashboard = QPushButton("Accueil")
        btn_dashboard.setObjectName("menuButton")
        btn_dashboard.clicked.connect(lambda: self.show_page("dashboard"))

        btn_physical = QPushButton("Capteurs physiques")
        btn_physical.setObjectName("menuButton")
        btn_physical.clicked.connect(lambda: self.show_page("physical"))

        btn_soft = QPushButton("Capteurs logiciels")
        btn_soft.setObjectName("menuButton")
        btn_soft.clicked.connect(lambda: self.show_page("soft"))

        btn_trends = QPushButton("Tendances")
        btn_trends.setObjectName("menuButton")
        btn_trends.clicked.connect(lambda: self.show_page("trends"))

        btn_alarms = QPushButton("Alarmes")
        btn_alarms.setObjectName("menuButton")
        btn_alarms.clicked.connect(lambda: self.show_page("alarms"))

        btn_reports = QPushButton("Rapports")
        btn_reports.setObjectName("menuButton")
        btn_reports.clicked.connect(lambda: self.show_page("reports"))

        layout.addWidget(menu_title)
        layout.addWidget(btn_dashboard)
        layout.addWidget(btn_physical)
        layout.addWidget(btn_soft)
        layout.addWidget(btn_trends)
        layout.addWidget(btn_alarms)
        layout.addWidget(btn_reports)
        layout.addStretch()

        return sidebar

    def show_page(self, name):
        page = self.pages[name]
        if hasattr(page, "refresh_page"):
            page.refresh_page()
        self.stack.setCurrentWidget(page)