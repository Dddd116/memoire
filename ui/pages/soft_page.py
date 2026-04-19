from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QHBoxLayout, QProgressBar, QScrollArea
)


class SoftPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(18)

        self.colors = {
            "primary": "#0a0e27",
            "secondary": "#131b3c",
            "tertiary": "#1e2a5e",
            "accent": "#00d4ff",
            "success": "#00ff88",
            "warning": "#ffaa00",
            "danger": "#ffffff",
            "info": "#4ecdc4",
            "text": "#ffffff",
            "text_muted": "#b8c1d9",
            "card_bg": "#16213e"
        }

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()

            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_sub_layout(child_layout)

    def clear_sub_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()

            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_sub_layout(child_layout)

    def get_status_style(self, status):
        if status == "normal":
            return "NORMAL", self.colors["success"]
        elif status == "attention":
            return "ATTENTION", self.colors["warning"]
        else:
            return "CRITIQUE", self.colors["danger"]

    def create_card(self, name, sensor, value, status):
        status_text, status_color = self.get_status_style(status)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors["tertiary"]};
                border: 1px solid #2c3e78;
                border-radius: 16px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: {self.colors["text"]};
            font-size: 18px;
            font-weight: bold;
            border: none;
        """)

        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet(f"""
            color: {status_color};
            font-size: 13px;
            font-weight: bold;
            background-color: transparent;
            border: none;
        """)

        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)

        value_label = QLabel(f"{value:.2f} {sensor.unit}")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"""
            color: {status_color};
            font-size: 28px;
            font-weight: bold;
            border: none;
            padding: 10px;
        """)

        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(int(sensor.max_val))
        progress.setValue(int(value))
        progress.setFormat(f"{int(value)} / {int(sensor.max_val)}")
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {self.colors["primary"]};
                color: white;
                border: 1px solid #3a4d8f;
                border-radius: 8px;
                text-align: center;
                height: 22px;
                font-size: 11px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {status_color};
                border-radius: 8px;
            }}
        """)

        card_layout.addLayout(header_layout)
        card_layout.addWidget(value_label)
        card_layout.addWidget(progress)

        return card

    def refresh_page(self):
        self.clear_layout()

        title = QLabel("CAPTEURS LOGICIELS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {self.colors["text"]};
            font-size: 24px;
            font-weight: bold;
            padding: 12px;
        """)

        self.layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(20)

        physical = {
            name: sensor["value"]
            for name, sensor in self.main_window.db.physical_sensors.items()
        }

        for name, sensor in self.main_window.db.soft_sensors.items():
            value = sensor.calculate(physical)
            status = sensor.get_status()

            card = self.create_card(name, sensor, value, status)
            container_layout.addWidget(card)

        container_layout.addStretch()
        scroll.setWidget(container)
        self.layout.addWidget(scroll)