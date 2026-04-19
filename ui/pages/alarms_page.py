from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFrame, QGridLayout, QSizePolicy,
    QLabel, QHBoxLayout
)


class AlarmsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.colors = {
            "bg": "#0a0f1f",
            "panel": "#11182c",
            "card": "#18243f",
            "card_soft": "#1c2b4a",
            "accent": "#00d4ff",
            "success": "#00e676",
            "warning": "#ffb300",
            "danger": "#ff4d6d",
            "text": "#ffffff",
            "muted": "#a8b3cf",
            "list_bg": "#0f1729",
            "button": "#00cfff",
            "button_hover": "#38dcff"
        }

        self.setObjectName("alarmsPage")
        self.setStyleSheet(f"""
            QWidget#alarmsPage {{
                background-color: {self.colors["bg"]};
                font-family: 'Segoe UI', Arial, sans-serif;
                color: {self.colors["text"]};
            }}

            QFrame#headerCard {{
                background-color: {self.colors["panel"]};
                border: none;
                border-radius: 26px;
            }}

            QFrame#statCard {{
                background-color: {self.colors["card"]};
                border: none;
                border-radius: 22px;
            }}

            QFrame#contentCard {{
                background-color: {self.colors["panel"]};
                border: none;
                border-radius: 26px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}

            QLabel#pageTitle {{
                color: {self.colors["accent"]};
                font-size: 42px;
                font-weight: 900;
                letter-spacing: 1px;
            }}

            QLabel#cardTitle {{
                color: {self.colors["muted"]};
                font-size: 18px;
                font-weight: 700;
            }}

            QLabel#cardValue {{
                font-size: 36px;
                font-weight: 900;
            }}

            QLabel#sectionTitle {{
                color: {self.colors["text"]};
                font-size: 24px;
                font-weight: 800;
            }}

            QLabel#statusMessage {{
                color: {self.colors["accent"]};
                font-size: 15px;
                font-weight: 700;
                background: transparent;
                border: none;
                padding-top: 4px;
                padding-bottom: 4px;
            }}

            QListWidget {{
                background-color: {self.colors["list_bg"]};
                color: {self.colors["text"]};
                border: none;
                border-radius: 18px;
                padding: 12px;
                font-size: 15px;
                outline: none;
            }}

            QListWidget::item {{
                background-color: transparent;
                border: none;
                padding: 10px 8px;
                margin: 4px 0px;
            }}

            QListWidget::item:selected {{
                background-color: {self.colors["card_soft"]};
                border-radius: 10px;
            }}

            QPushButton#refreshButton {{
                background-color: {self.colors["button"]};
                color: #061019;
                border: none;
                border-radius: 16px;
                padding: 14px 24px;
                font-size: 15px;
                font-weight: 800;
                min-width: 180px;
            }}

            QPushButton#refreshButton:hover {{
                background-color: {self.colors["button_hover"]};
            }}

            QPushButton#refreshButton:pressed {{
                padding-top: 15px;
            }}
        """)

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(26, 24, 26, 24)
        self.layout.setSpacing(20)

        self.layout.addWidget(self.create_header_card())
        self.layout.addWidget(self.create_stats_section())
        self.layout.addWidget(self.create_alarms_card())
        self.layout.addStretch()

    def create_header_card(self):
        header_card = QFrame()
        header_card.setObjectName("headerCard")

        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(10)

        title = QLabel("ALARMES")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)

        self.status_message = QLabel("Aucune vérification effectuée.")
        self.status_message.setObjectName("statusMessage")
        self.status_message.setAlignment(Qt.AlignCenter)
        self.status_message.setWordWrap(True)

        header_layout.addWidget(title)
        header_layout.addWidget(self.status_message)

        return header_card

    def create_stats_section(self):
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        self.normal_card = self.create_stat_card("État normal", "0", self.colors["success"])
        self.warning_card = self.create_stat_card("Alerte", "0", self.colors["warning"])
        self.critical_card = self.create_stat_card("Critique", "0", self.colors["danger"])

        grid.addWidget(self.normal_card["frame"], 0, 0)
        grid.addWidget(self.warning_card["frame"], 0, 1)
        grid.addWidget(self.critical_card["frame"], 0, 2)

        return container

    def create_stat_card(self, title, value, color):
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setMinimumHeight(160)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"""
            color: {color};
            font-size: 40px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        return {
            "frame": frame,
            "title_label": title_label,
            "value_label": value_label
        }

    def create_alarms_card(self):
        alarms_card = QFrame()
        alarms_card.setObjectName("contentCard")

        alarms_layout = QVBoxLayout(alarms_card)
        alarms_layout.setContentsMargins(24, 22, 24, 22)
        alarms_layout.setSpacing(16)

        self.middle_title = QLabel("LISTE DES ALARMES ACTIVES")
        self.middle_title.setObjectName("sectionTitle")
        self.middle_title.setAlignment(Qt.AlignCenter)

        self.alarm_list = QListWidget()
        self.alarm_list.setMinimumHeight(320)

        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.refresh_page)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.refresh_button)
        button_row.addStretch()

        alarms_layout.addWidget(self.middle_title)
        alarms_layout.addWidget(self.alarm_list)
        alarms_layout.addLayout(button_row)

        return alarms_card

    def refresh_page(self):
        self.alarm_list.clear()

        physical = {
            name: sensor["value"]
            for name, sensor in self.main_window.db.physical_sensors.items()
        }

        normal_count = 0
        warning_count = 0
        critical_count = 0
        has_alarm = False

        for name, sensor in self.main_window.db.soft_sensors.items():
            value = sensor.calculate(physical)
            status = sensor.get_status()

            if status == "normal":
                normal_count += 1
            elif status == "attention":
                warning_count += 1
            else:
                critical_count += 1

            if status != "normal":
                has_alarm = True
                current_time = datetime.now().strftime("%H:%M:%S")
                text = f"[{current_time}] {name}: {value:.2f} {sensor.unit}"

                item = QListWidgetItem(text)

                if status == "critique":
                    item.setForeground(QColor(self.colors["danger"]))
                else:
                    item.setForeground(QColor(self.colors["warning"]))

                self.alarm_list.addItem(item)

        self.normal_card["value_label"].setText(str(normal_count))
        self.warning_card["value_label"].setText(str(warning_count))
        self.critical_card["value_label"].setText(str(critical_count))

        if not has_alarm:
            item = QListWidgetItem("✅ Aucune alarme active")
            item.setForeground(QColor(self.colors["success"]))
            self.alarm_list.addItem(item)
            self.status_message.setText("Aucune alarme active.")
        else:
            self.status_message.setText(
                f"Nombre d'alertes : {warning_count} | Nombre d'alarmes critiques : {critical_count}"
            )