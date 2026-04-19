from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QHeaderView
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class TrendsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.colors = {
            "page_bg": "#16213e",
            "card_1": "#1f2a56",
            "card_2": "#243162",
            "accent": "#00d4ff",
            "warning": "#ffaa00",
            "danger": "#ff5252",
            "text": "#ffffff",
            "muted": "#c7d2ea"
        }

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors["page_bg"]};
                color: {self.colors["text"]};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}

            QLabel {{
                border: none;
                background: transparent;
            }}

            QFrame#topCard {{
                background-color: {self.colors["card_1"]};
                border: none;
                border-radius: 24px;
            }}

            QFrame#chartCard {{
                background-color: {self.colors["card_2"]};
                border: none;
                border-radius: 24px;
            }}

            QFrame#tableCard {{
                background-color: {self.colors["card_1"]};
                border: none;
                border-radius: 24px;
            }}

            QLabel#pageTitle {{
                color: {self.colors["accent"]};
                font-size: 34px;
                font-weight: 800;
            }}

            QLabel#fieldLabel {{
                color: {self.colors["text"]};
                font-size: 18px;
                font-weight: 700;
            }}

            QLabel#infoLabel {{
                color: {self.colors["muted"]};
                font-size: 17px;
                font-weight: 500;
            }}

            QComboBox {{
                background-color: #1b2550;
                color: {self.colors["text"]};
                border: none;
                border-radius: 14px;
                padding: 12px 14px;
                font-size: 17px;
                min-height: 32px;
            }}

            QComboBox::drop-down {{
                border: none;
            }}

            QPushButton {{
                background-color: {self.colors["accent"]};
                color: black;
                border: none;
                border-radius: 14px;
                padding: 14px 18px;
                font-size: 17px;
                font-weight: 700;
                min-height: 34px;
            }}

            QPushButton:hover {{
                background-color: #4ce2ff;
            }}

            QTableWidget {{
                background-color: #1b2550;
                color: {self.colors["text"]};
                border: none;
                border-radius: 18px;
                padding: 8px;
                font-size: 16px;
                gridline-color: transparent;
            }}

            QTableWidget::item {{
                padding: 10px;
            }}

            QHeaderView::section {{
                background-color: #243162;
                color: {self.colors["text"]};
                border: none;
                padding: 12px;
                font-size: 16px;
                font-weight: 700;
            }}
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(22, 22, 22, 22)
        self.layout.setSpacing(18)

        self.build_ui()

    def build_ui(self):
        title = QLabel("TENDANCES")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        self.top_card = QFrame()
        self.top_card.setObjectName("topCard")
        self.top_layout = QHBoxLayout(self.top_card)
        self.top_layout.setContentsMargins(20, 18, 20, 18)
        self.top_layout.setSpacing(14)

        self.sensor_label = QLabel("Capteur")
        self.sensor_label.setObjectName("fieldLabel")

        self.sensor_combo = QComboBox()

        self.period_label = QLabel("Période")
        self.period_label.setObjectName("fieldLabel")

        self.period_combo = QComboBox()
        self.period_combo.addItems(["7", "15", "30"])

        self.show_button = QPushButton("Afficher")
        self.show_button.clicked.connect(self.update_trend)

        self.top_layout.addWidget(self.sensor_label)
        self.top_layout.addWidget(self.sensor_combo, 2)
        self.top_layout.addWidget(self.period_label)
        self.top_layout.addWidget(self.period_combo, 1)
        self.top_layout.addWidget(self.show_button, 1)

        self.layout.addWidget(self.top_card)

        self.chart_card = QFrame()
        self.chart_card.setObjectName("chartCard")
        self.chart_layout = QVBoxLayout(self.chart_card)
        self.chart_layout.setContentsMargins(20, 18, 20, 18)
        self.chart_layout.setSpacing(12)

        self.figure = Figure(figsize=(8, 4), facecolor=self.colors["card_2"])
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        self.chart_layout.addWidget(self.canvas)
        self.layout.addWidget(self.chart_card, 2)

        self.table_card = QFrame()
        self.table_card.setObjectName("tableCard")
        self.table_layout = QVBoxLayout(self.table_card)
        self.table_layout.setContentsMargins(20, 18, 20, 18)
        self.table_layout.setSpacing(12)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Date / Heure", "Valeur"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)

        self.info_label = QLabel("Choisissez un capteur.")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setAlignment(Qt.AlignCenter)

        self.table_layout.addWidget(self.table)
        self.table_layout.addWidget(self.info_label)

        self.layout.addWidget(self.table_card, 1)

    def refresh_page(self):
        self.sensor_combo.clear()

        physical_options = [
            f"{name} (Physique)"
            for name in self.main_window.db.physical_sensors.keys()
        ]
        soft_options = [
            f"{name} (Logiciel)"
            for name in self.main_window.db.soft_sensors.keys()
        ]

        self.sensor_combo.addItems(physical_options + soft_options)

        if self.sensor_combo.count() > 0:
            self.update_trend()
        else:
            self.clear_chart_and_table("Aucun capteur disponible.")

    def clear_chart_and_table(self, message):
        self.ax.clear()
        self.ax.set_facecolor("#1b2550")
        self.ax.set_title(message, color="white", fontsize=15, fontweight="bold")
        self.ax.tick_params(colors="white", labelsize=11)
        self.canvas.draw()

        self.table.setRowCount(0)
        self.info_label.setText(message)

    def update_trend(self):
        sensor_text = self.sensor_combo.currentText()
        if not sensor_text:
            self.clear_chart_and_table("Aucun capteur sélectionné.")
            return

        try:
            days = int(self.period_combo.currentText())
        except ValueError:
            days = 7

        is_soft = "(Logiciel)" in sensor_text
        sensor_name = sensor_text.replace(" (Physique)", "").replace(" (Logiciel)", "")

        timestamps, values = self.main_window.db.get_history(sensor_name, days)

        self.ax.clear()
        self.ax.set_facecolor("#1b2550")

        if timestamps and values:
            x_values = list(range(len(values)))

            self.ax.plot(
                x_values,
                values,
                linewidth=2.8,
                marker="o",
                markersize=5,
                color=self.colors["accent"]
            )

            self.ax.fill_between(
                x_values,
                values,
                alpha=0.25,
                color=self.colors["accent"]
            )

            if is_soft and sensor_name in self.main_window.db.soft_sensors:
                sensor = self.main_window.db.soft_sensors[sensor_name]

                self.ax.axhline(
                    y=sensor.max_val * 0.6,
                    linestyle="--",
                    linewidth=1.8,
                    color=self.colors["warning"],
                    alpha=0.8,
                    label="Attention"
                )

                self.ax.axhline(
                    y=sensor.max_val * 0.8,
                    linestyle="--",
                    linewidth=1.8,
                    color=self.colors["danger"],
                    alpha=0.8,
                    label="Critique"
                )

                legend = self.ax.legend(loc="upper right", fontsize=10)
                if legend is not None:
                    legend.get_frame().set_facecolor("#243162")
                    legend.get_frame().set_edgecolor("none")
                    for text in legend.get_texts():
                        text.set_color("white")

            self.ax.set_title(
                f"Tendance - {sensor_name}",
                color="white",
                fontsize=16,
                fontweight="bold"
            )
            self.ax.set_xlabel("Historique", color="white", fontsize=12)
            self.ax.set_ylabel("Valeur", color="white", fontsize=12)
            self.ax.tick_params(colors="white", labelsize=11)
            self.ax.grid(True, alpha=0.15, color="white")

            recent_data = list(zip(timestamps[-15:], values[-15:]))
            self.table.setRowCount(len(recent_data))

            for i, (t, v) in enumerate(recent_data):
                self.table.setItem(i, 0, QTableWidgetItem(str(t)[:16]))
                self.table.setItem(i, 1, QTableWidgetItem(f"{float(v):.2f}"))

            self.info_label.setText(f"Données sauvegardées du capteur : {sensor_name}")
        else:
            self.table.setRowCount(0)
            self.ax.set_title(
                "Aucune donnée sauvegardée",
                color="white",
                fontsize=15,
                fontweight="bold"
            )
            self.ax.tick_params(colors="white", labelsize=11)
            self.info_label.setText("Aucune donnée disponible pour ce capteur.")

        self.canvas.draw()