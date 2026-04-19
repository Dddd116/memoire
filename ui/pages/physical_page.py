# -*- coding: utf-8 -*-
import random

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QFrame, QHBoxLayout, QScrollArea,
    QGridLayout, QSizePolicy, QGraphicsDropShadowEffect
)


class PhysicalPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.value_labels = {}
        self.pending_values = {}

        self.colors = {
            "bg": "#0f172a",
            "card": "#1e293b",
            "card_alt": "#22304a",
            "accent": "#7dd3fc",
            "accent_soft": "#bae6fd",
            "success": "#86efac",
            "text": "#f8fafc",
            "muted": "#cbd5e1",
            "soft": "#94a3b8",
            "button_dark": "#1a2540",
            "button_hover": "#243552"
        }

        self.setObjectName("physicalPage")
        self.apply_styles()

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(28, 24, 28, 20)
        self._root.setSpacing(0)

    def apply_styles(self):
        self.setStyleSheet(f"""
            QWidget#physicalPage {{
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

            QScrollBar:vertical {{
                background: transparent;
                width: 7px;
                margin: 6px 0;
            }}

            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.14);
                border-radius: 3px;
                min-height: 28px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QLabel {{
                border: none;
                background: transparent;
            }}

            QFrame#sensorCard,
            QFrame#sensorCardAlt {{
                background-color: {self.colors["card"]};
                border: none;
                border-radius: 24px;
            }}

            QFrame#sensorCardAlt {{
                background-color: {self.colors["card_alt"]};
            }}

            QLabel#pageTitle {{
                color: {self.colors["text"]};
                font-size: 30px;
                font-weight: 800;
            }}

            QLabel#sensorName {{
                color: {self.colors["text"]};
                font-size: 16px;
                font-weight: 700;
            }}

            QLabel#sensorRange {{
                color: #082f49;
                font-size: 11px;
                font-weight: 700;
                padding: 5px 12px;
                border-radius: 12px;
                background-color: {self.colors["accent"]};
            }}

            QLabel#sensorValue {{
                color: {self.colors["accent"]};
                font-size: 38px;
                font-weight: 800;
            }}

            QLabel#sensorUnit {{
                color: {self.colors["accent_soft"]};
                font-size: 13px;
                font-weight: 600;
            }}

            QLabel#stepInfo {{
                color: {self.colors["soft"]};
                font-size: 11px;
                font-weight: 600;
            }}

            QPushButton#minusButton {{
                background-color: {self.colors["button_dark"]};
                color: {self.colors["text"]};
                border: none;
                border-radius: 14px;
                font-size: 22px;
                font-weight: 500;
                min-width: 50px;
                max-width: 50px;
                min-height: 44px;
                max-height: 44px;
            }}

            QPushButton#minusButton:hover {{
                background-color: {self.colors["button_hover"]};
            }}

            QPushButton#plusButton {{
                background-color: rgba(125, 211, 252, 0.18);
                color: {self.colors["accent"]};
                border: none;
                border-radius: 14px;
                font-size: 22px;
                font-weight: 700;
                min-width: 50px;
                max-width: 50px;
                min-height: 44px;
                max-height: 44px;
            }}

            QPushButton#plusButton:hover {{
                background-color: rgba(125, 211, 252, 0.28);
            }}

            QPushButton#saveButton {{
                background-color: {self.colors["accent"]};
                color: #082f49;
                border: none;
                border-radius: 14px;
                padding: 0 30px;
                min-height: 50px;
                font-size: 14px;
                font-weight: 800;
            }}

            QPushButton#saveButton:hover {{
                background-color: #a5e3fb;
            }}

            QPushButton#simulateButton {{
                background-color: rgba(134, 239, 172, 0.14);
                color: {self.colors["success"]};
                border: none;
                border-radius: 14px;
                padding: 0 30px;
                min-height: 50px;
                font-size: 14px;
                font-weight: 800;
            }}

            QPushButton#simulateButton:hover {{
                background-color: rgba(134, 239, 172, 0.24);
            }}

            QFrame#separator {{
                background: rgba(255,255,255,0.08);
                border: none;
                max-height: 1px;
            }}
        """)

    def _sep(self):
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFixedHeight(1)
        return sep

    def _shadow(self):
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(24)
        effect.setOffset(0, 6)
        color = QColor(0, 0, 0, 70)
        effect.setColor(color)
        return effect

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

    def compute_step(self, sensor):
        span = sensor["max"] - sensor["min"]
        step = span / 50.0

        if step < 0.01:
            return 0.01
        elif step < 0.1:
            return 0.1
        elif step < 1:
            return 0.5
        return round(step, 1)

    def update_value_label(self, key):
        value = self.pending_values[key]
        self.value_labels[key].setText(f"{value:.2f}")

    def change_value(self, key, direction):
        sensor = self.main_window.db.physical_sensors[key]
        step = self.compute_step(sensor)
        new_value = self.pending_values[key] + direction * step
        new_value = max(sensor["min"], min(sensor["max"], round(new_value, 4)))
        self.pending_values[key] = new_value
        self.update_value_label(key)

    def create_sensor_card(self, key, sensor, alt=False):
        object_name = "sensorCardAlt" if alt else "sensorCard"

        card = QFrame()
        card.setObjectName(object_name)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        card.setMinimumHeight(210)
        card.setGraphicsEffect(self._shadow())

        outer = QVBoxLayout(card)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        name_label = QLabel(sensor["name"])
        name_label.setObjectName("sensorName")

        range_label = QLabel(f'{sensor["min"]} - {sensor["max"]} {sensor["unit"]}')
        range_label.setObjectName("sensorRange")
        range_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(range_label)

        outer.addLayout(header_layout)
        outer.addSpacing(8)

        value_label = QLabel(f'{self.pending_values[key]:.2f}')
        value_label.setObjectName("sensorValue")
        value_label.setAlignment(Qt.AlignCenter)
        self.value_labels[key] = value_label

        unit_label = QLabel(sensor["unit"])
        unit_label.setObjectName("sensorUnit")
        unit_label.setAlignment(Qt.AlignCenter)

        outer.addWidget(value_label)
        outer.addWidget(unit_label)
        outer.addStretch()

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)

        step = self.compute_step(sensor)
        step_label = QLabel(f"Pas : {step} {sensor['unit']}")
        step_label.setObjectName("stepInfo")

        minus_button = QPushButton("-")
        minus_button.setObjectName("minusButton")
        minus_button.setCursor(Qt.PointingHandCursor)
        minus_button.clicked.connect(lambda _, k=key: self.change_value(k, -1))

        plus_button = QPushButton("+")
        plus_button.setObjectName("plusButton")
        plus_button.setCursor(Qt.PointingHandCursor)
        plus_button.clicked.connect(lambda _, k=key: self.change_value(k, 1))

        controls_layout.addWidget(step_label)
        controls_layout.addStretch()
        controls_layout.addWidget(minus_button)
        controls_layout.addWidget(plus_button)

        outer.addLayout(controls_layout)

        return card

    def refresh_page(self):
        self.clear_layout(self._root)

        self.value_labels = {}
        self.pending_values = {
            key: sensor["value"]
            for key, sensor in self.main_window.db.physical_sensors.items()
        }

        title = QLabel("CAPTEURS PHYSIQUES")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)

        self._root.addWidget(title)
        self._root.addSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(0)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        items = list(self.main_window.db.physical_sensors.items())

        for index, (key, sensor) in enumerate(items):
            card = self.create_sensor_card(key, sensor, alt=(index % 2 == 1))
            row = index // 2
            col = index % 2
            grid.addWidget(card, row, col)

        if len(items) % 2 == 1:
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            grid.addWidget(spacer, len(items) // 2, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        container_layout.addLayout(grid)
        container_layout.addStretch()

        scroll.setWidget(container)
        self._root.addWidget(scroll, stretch=1)

        self._root.addSpacing(16)
        self._root.addWidget(self._build_footer())

    def _build_footer(self):
        wrapper = QWidget()
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        simulate_button = QPushButton("Simulation aléatoire")
        simulate_button.setObjectName("simulateButton")
        simulate_button.setCursor(Qt.PointingHandCursor)
        simulate_button.setFixedHeight(50)
        simulate_button.clicked.connect(self.auto_simulate)

        save_button = QPushButton("Enregistrer")
        save_button.setObjectName("saveButton")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setFixedHeight(50)
        save_button.clicked.connect(self.update_values)

        row.addStretch()
        row.addWidget(simulate_button)
        row.addWidget(save_button)
        row.addStretch()

        return wrapper

    def update_values(self):
        values = {}

        for key, sensor in self.main_window.db.physical_sensors.items():
            sensor["value"] = self.pending_values[key]
            values[key] = sensor["value"]

        soft_values = {
            name: sensor.calculate(values)
            for name, sensor in self.main_window.db.soft_sensors.items()
        }

        self.main_window.db.add_measurement(values, soft_values)

        QMessageBox.information(
            self,
            "Succès",
            "Les valeurs ont été mises à jour."
        )

        self.main_window.show_page("soft")

    def auto_simulate(self):
        for key, sensor in self.main_window.db.physical_sensors.items():
            self.pending_values[key] = round(
                random.uniform(sensor["min"], sensor["max"]), 2
            )
            self.update_value_label(key)