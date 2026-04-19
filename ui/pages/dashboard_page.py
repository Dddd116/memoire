from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QHBoxLayout, QGridLayout, QScrollArea, QSizePolicy
)


class DashboardPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.colors = {
            "bg": "#0b1220",
            "panel": "#121c31",

            "card_blue": "rgba(96, 165, 250, 0.22)",
            "card_blue_alt": "rgba(147, 197, 253, 0.18)",

            "accent": "#93C5FD",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "danger": "#ef4444",

            "text": "#ffffff",
            "muted": "#DBEAFE",
            "soft": "#BFDBFE",
        }

        self.setObjectName("dashboardPage")
        self.setStyleSheet(f"""
            QWidget#dashboardPage {{
                background-color: {self.colors["bg"]};
                color: {self.colors["text"]};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}

            QScrollArea {{
                border: none;
                background: transparent;
            }}

            QScrollArea > QWidget > QWidget {{
                background: transparent;
                border: none;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}

            QLabel#pageTitle {{
                color: {self.colors["accent"]};
                font-size: 34px;
                font-weight: 900;
                letter-spacing: 1px;
            }}

            QFrame#cardsSection {{
                background-color: rgba(147, 197, 253, 0.10);
                border: none;
                border-radius: 28px;
            }}

            QFrame#sectionBlock {{
                background-color: {self.colors["card_blue"]};
                border: none;
                border-radius: 24px;
            }}

            QFrame#valueCardAlt {{
                background-color: {self.colors["card_blue_alt"]};
                border: none;
                border-radius: 24px;
            }}

            QLabel#listText {{
                color: {self.colors["text"]};
                font-size: 15px;
                font-weight: 600;
                padding-top: 4px;
                padding-bottom: 4px;
            }}
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(28, 24, 28, 24)
        self.layout.setSpacing(20)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)

    def status_info(self, status):
        if status == "normal":
            return "NORMAL", self.colors["success"], "rgba(34,197,94,0.20)"
        elif status == "attention":
            return "ATTENTION", self.colors["warning"], "rgba(245,158,11,0.22)"
        return "CRITIQUE", self.colors["danger"], "rgba(239,68,68,0.22)"

    def create_cards_section(self):
        frame = QFrame()
        frame.setObjectName("cardsSection")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(18)

        return frame, layout

    def create_value_card(self, name, value, unit, status, alt=False):
        status_text, status_color, status_bg = self.status_info(status)
        bg_color = self.colors["card_blue_alt"] if alt else self.colors["card_blue"]

        card = QFrame()
        card.setMinimumHeight(220)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: none;
                border-radius: 22px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                border-radius: 0px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        h_row = QHBoxLayout(header)
        h_row.setContentsMargins(22, 16, 22, 14)
        h_row.setSpacing(10)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            f"color: {self.colors['text']}; font-size: 19px; font-weight: 900;"
        )

        badge = QLabel(status_text)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            color: {status_color};
            background-color: {status_bg};
            border: none;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 900;
            padding: 6px 14px;
        """)

        h_row.addWidget(name_lbl)
        h_row.addStretch()
        h_row.addWidget(badge)
        outer.addWidget(header)

        body = QVBoxLayout()
        body.setContentsMargins(22, 16, 22, 20)
        body.setSpacing(6)
        body.addStretch()

        val_lbl = QLabel(f"{value:.2f}")
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet(
            f"color: {self.colors['text']}; font-size: 44px; font-weight: 900; "
            f"letter-spacing: -1px; border: none;"
        )

        unit_lbl = QLabel(unit)
        unit_lbl.setAlignment(Qt.AlignCenter)
        unit_lbl.setStyleSheet(
            f"color: {self.colors['soft']}; font-size: 14px; font-weight: 700; border: none;"
        )

        body.addWidget(val_lbl)
        body.addWidget(unit_lbl)
        body.addStretch()
        outer.addLayout(body)

        return card

    def create_text_block(self, lines, alt=False):
        block = QFrame()
        block.setObjectName("valueCardAlt" if alt else "sectionBlock")
        block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(block)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        for line in lines:
            lbl = QLabel(line)
            lbl.setObjectName("listText")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        layout.addStretch()
        return block

    def refresh_page(self):
        self.clear_layout(self.layout)

        title = QLabel("ACCUEIL")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 6, 0, 6)
        container_layout.setSpacing(22)

        physical = {
            name: sensor["value"]
            for name, sensor in self.main_window.db.physical_sensors.items()
        }

        for sensor in self.main_window.db.soft_sensors.values():
            sensor.calculate(physical)

        cards_section, cards_section_layout = self.create_cards_section()

        cards_grid = QGridLayout()
        cards_grid.setHorizontalSpacing(20)
        cards_grid.setVerticalSpacing(20)

        wanted_names = ["MES", "DCO", "DBO", "qualit"]
        found_sensors = []

        for wanted in wanted_names:
            for name, sensor in self.main_window.db.soft_sensors.items():
                if wanted.lower() in name.lower():
                    if not any(existing_name == name for existing_name, _ in found_sensors):
                        found_sensors.append((name, sensor))
                        break

        for index, (name, sensor) in enumerate(found_sensors):
            card = self.create_value_card(
                name=name,
                value=sensor.current_value,
                unit=sensor.unit,
                status=sensor.get_status(),
                alt=(index % 2 == 1),
            )
            cards_grid.addWidget(card, index // 2, index % 2)

        cards_grid.setColumnStretch(0, 1)
        cards_grid.setColumnStretch(1, 1)
        cards_section_layout.addLayout(cards_grid)
        container_layout.addWidget(cards_section)

        normal_count = 0
        attention_count = 0
        critique_count = 0

        for sensor in self.main_window.db.soft_sensors.values():
            status = sensor.get_status()
            if status == "normal":
                normal_count += 1
            elif status == "attention":
                attention_count += 1
            else:
                critique_count += 1

        summary_lines = [
            f"Capteurs logiciels : {len(self.main_window.db.soft_sensors)}",
            f"Normal : {normal_count}",
            f"Attention : {attention_count}",
            f"Critique : {critique_count}",
        ]

        flow_lines = []
        for soft_name, sensor in self.main_window.db.soft_sensors.items():
            inputs = [
                self.main_window.db.physical_sensors[i]["name"]
                for i in sensor.physical_inputs
            ]
            inputs_text = " + ".join(inputs) if inputs else "Aucune entrée"
            flow_lines.append(f"{soft_name} ← {inputs_text}")

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        bottom_row.addWidget(self.create_text_block(summary_lines, alt=False), 1)
        bottom_row.addWidget(self.create_text_block(flow_lines, alt=True), 2)

        container_layout.addLayout(bottom_row)
        container_layout.addStretch()

        scroll.setWidget(container)
        self.layout.addWidget(scroll)