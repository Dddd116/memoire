from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QGridLayout,
    QSizePolicy
)


class ReportsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.colors = {
            "bg": "#0f172a",
            "panel": "#16213e",
            "card": "#1e293b",
            "card_hover": "#243552",
            "accent": "#7dd3fc",
            "accent_soft": "#bae6fd",
            "success": "#86efac",
            "success_hover": "#bbf7d0",
            "text": "#f8fafc",
            "muted": "#cbd5e1"
        }

        self.setObjectName("reportsPage")
        self.setStyleSheet(f"""
            QWidget#reportsPage {{
                background-color: {self.colors["bg"]};
                font-family: 'Segoe UI', Arial, sans-serif;
                color: {self.colors["text"]};
            }}

            QFrame#actionCard {{
                background-color: {self.colors["card"]};
                border: none;
                border-radius: 22px;
            }}

            QLabel {{
                border: none;
                background: transparent;
            }}

            QLabel#mainTitle {{
                color: {self.colors["text"]};
                font-size: 32px;
                font-weight: 800;
            }}

            QLabel#cardTitle {{
                color: {self.colors["text"]};
                font-size: 20px;
                font-weight: 700;
            }}

            QPushButton#csvButton {{
                background-color: {self.colors["success"]};
                color: #052e16;
                border: none;
                border-radius: 14px;
                padding: 14px 18px;
                font-size: 14px;
                font-weight: 800;
            }}

            QPushButton#csvButton:hover {{
                background-color: {self.colors["success_hover"]};
            }}

            QPushButton#pdfButton {{
                background-color: {self.colors["accent"]};
                color: #082f49;
                border: none;
                border-radius: 14px;
                padding: 14px 18px;
                font-size: 14px;
                font-weight: 800;
            }}

            QPushButton#pdfButton:hover {{
                background-color: {self.colors["accent_soft"]};
            }}
        """)

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(28, 24, 28, 24)
        self.layout.setSpacing(20)

        self.title_label = QLabel("RAPPORTS")
        self.title_label.setObjectName("mainTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.layout.addWidget(self.create_actions_section())
        self.layout.addStretch()

    def create_actions_section(self):
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        csv_card = self.create_action_card(
            title="EXPORT CSV",
            button_text="EXPORTER CSV",
            button_name="csvButton",
            button_action=self.export_csv
        )

        pdf_card = self.create_action_card(
            title="RAPPORT PDF",
            button_text="GÉNÉRER PDF",
            button_name="pdfButton",
            button_action=self.export_pdf
        )

        grid.addWidget(csv_card, 0, 0)
        grid.addWidget(pdf_card, 0, 1)

        return container

    def create_action_card(self, title, button_text, button_name, button_action):
        card = QFrame()
        card.setObjectName("actionCard")
        card.setMinimumHeight(220)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignCenter)

        button = QPushButton(button_text)
        button.setObjectName(button_name)
        button.setMinimumHeight(50)
        button.clicked.connect(button_action)

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(button)

        return card

    def refresh_page(self):
        pass

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter CSV",
            "sensors_data.csv",
            "CSV Files (*.csv)"
        )

        if filename:
            try:
                self.main_window.db.save_history_as(filename)
                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"Le fichier CSV a été exporté avec succès :\n{filename}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de l'export CSV :\n{str(e)}"
                )

    def export_pdf(self):
        QMessageBox.information(
            self,
            "Rapport PDF",
            "La génération du rapport PDF n'est pas encore implémentée."
        )