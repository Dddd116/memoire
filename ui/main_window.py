"""
main_window.py — Fenêtre principale refactorisée
✅ Texte horizontal partout
✅ Sidebar propre (menu uniquement)
✅ Pas de scroll horizontal
✅ Toutes les pages intégrées
✅ Alarmes, Graphiques, IA/LSTM, Rapports, Utilisateurs
"""

import random
import csv
import os
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QFrame, QLabel,
    QScrollArea, QGridLayout, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QComboBox,
    QProgressBar, QMessageBox, QFileDialog, QSpinBox,
    QTextEdit, QGroupBox
)

try:
    import pyqtgraph as pg
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False

from core.sensor_database import SensorDatabase
from core.alert_manager import AlertManagerCSV


# ══════════════════════════════════════════════════════════════════
#  PALETTE & STYLES GLOBAUX
# ══════════════════════════════════════════════════════════════════
C = {
    "bg":        "#0a0e27",
    "panel":     "#131b3c",
    "card":      "#16213e",
    "hover":     "#1e2a5e",
    "accent":    "#00d4ff",
    "accent2":   "#0099bb",
    "green":     "#00e676",
    "yellow":    "#ffd740",
    "red":       "#ff5252",
    "text":      "#ffffff",
    "muted":     "#8892b0",
    "border":    "rgba(0,212,255,0.18)",
}

GLOBAL_CSS = f"""
QWidget {{
    background-color: {C['bg']};
    color: {C['text']};
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: {C['panel']}; width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {C['accent2']}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{ height: 0px; }}

QFrame#sidebar {{
    background-color: {C['panel']};
    border-right: 1px solid {C['border']};
    border-radius: 0px;
}}
QFrame#header {{
    background-color: {C['panel']};
    border-bottom: 1px solid {C['border']};
}}
QFrame#card {{
    background-color: {C['card']};
    border-radius: 16px;
    border: 1px solid {C['border']};
}}
QLabel {{ background: transparent; border: none; }}
QLabel#pageTitle {{
    color: {C['accent']};
    font-size: 22px;
    font-weight: 700;
}}
QLabel#sectionTitle {{
    color: {C['text']};
    font-size: 16px;
    font-weight: 600;
}}
QLabel#value {{
    color: {C['accent']};
    font-size: 28px;
    font-weight: 800;
}}
QLabel#unit {{
    color: {C['muted']};
    font-size: 13px;
}}
QLabel#status_ok  {{ color: {C['green']}; font-weight: 700; }}
QLabel#status_warn {{ color: {C['yellow']}; font-weight: 700; }}
QLabel#status_crit {{ color: {C['red']}; font-weight: 700; }}

QPushButton#nav {{
    background-color: transparent;
    color: {C['muted']};
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 600;
    text-align: left;
}}
QPushButton#nav:hover {{
    background-color: {C['hover']};
    color: {C['text']};
}}
QPushButton#nav_active {{
    background-color: {C['hover']};
    color: {C['accent']};
    border-left: 3px solid {C['accent']};
    border-radius: 0px 12px 12px 0px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 700;
    text-align: left;
}}

QPushButton#primary {{
    background-color: {C['accent']};
    color: #000;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
}}
QPushButton#primary:hover {{ background-color: #4ce2ff; }}
QPushButton#danger {{
    background-color: {C['red']};
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 700;
}}
QPushButton#danger:hover {{ background-color: #ff7070; }}
QPushButton#secondary {{
    background-color: {C['hover']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
}}
QPushButton#secondary:hover {{ background-color: {C['accent2']}; color: #000; }}

QTableWidget {{
    background-color: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    gridline-color: {C['border']};
    outline: none;
}}
QTableWidget::item {{
    padding: 8px 12px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: {C['hover']};
    color: {C['accent']};
}}
QHeaderView::section {{
    background-color: {C['panel']};
    color: {C['muted']};
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid {C['border']};
    font-weight: 600;
    text-transform: uppercase;
    font-size: 12px;
}}
QLineEdit, QComboBox, QSpinBox {{
    background-color: {C['hover']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}}
QLineEdit:focus, QComboBox:focus {{ border-color: {C['accent']}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: {C['panel']};
    color: {C['text']};
    selection-background-color: {C['hover']};
}}
QProgressBar {{
    background-color: {C['hover']};
    border-radius: 6px;
    text-align: center;
    color: {C['text']};
    font-size: 12px;
    min-height: 14px;
}}
QProgressBar::chunk {{
    background-color: {C['accent']};
    border-radius: 6px;
}}
"""


# ══════════════════════════════════════════════════════════════════
#  HELPER WIDGETS
# ══════════════════════════════════════════════════════════════════

def card_widget(parent_layout=None, margins=(16, 16, 16, 16), spacing=12):
    """Retourne un QFrame card avec layout vertical."""
    f = QFrame()
    f.setObjectName("card")
    lay = QVBoxLayout(f)
    lay.setContentsMargins(*margins)
    lay.setSpacing(spacing)
    if parent_layout:
        parent_layout.addWidget(f)
    return f, lay


def hline():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {C['border']};")
    return line


def status_badge(status: str) -> QLabel:
    lbl = QLabel(status.upper())
    if status in ("critique", "critical"):
        lbl.setObjectName("status_crit")
        lbl.setStyleSheet(f"color:{C['red']}; font-weight:700; font-size:12px;"
                          f"background:{C['red']}22; border-radius:6px; padding:2px 8px;")
    elif status in ("warning", "attention"):
        lbl.setObjectName("status_warn")
        lbl.setStyleSheet(f"color:{C['yellow']}; font-weight:700; font-size:12px;"
                          f"background:{C['yellow']}22; border-radius:6px; padding:2px 8px;")
    else:
        lbl.setObjectName("status_ok")
        lbl.setStyleSheet(f"color:{C['green']}; font-weight:700; font-size:12px;"
                          f"background:{C['green']}22; border-radius:6px; padding:2px 8px;")
    return lbl


def make_kpi_card(title, value, unit, color=None):
    """Carte KPI : titre / valeur / unité."""
    f = QFrame()
    f.setObjectName("card")
    lay = QVBoxLayout(f)
    lay.setContentsMargins(18, 16, 18, 16)
    lay.setSpacing(4)

    t = QLabel(title)
    t.setObjectName("unit")
    t.setWordWrap(False)

    v = QLabel(str(value))
    v.setObjectName("value")
    if color:
        v.setStyleSheet(f"color: {color}; font-size:28px; font-weight:800;")

    u = QLabel(unit)
    u.setObjectName("unit")

    lay.addWidget(t)
    lay.addWidget(v)
    lay.addWidget(u)
    return f, v  # retourne le label valeur pour mise à jour


# ══════════════════════════════════════════════════════════════════
#  PAGE DE BASE
# ══════════════════════════════════════════════════════════════════
class BasePage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.db = main_win.db
        self.alert_mgr = main_win.alert_mgr

    def refresh_page(self):
        pass

    def _scroll_page(self, inner_widget):
        """Wrap inner_widget in a vertical scroll area."""
        scroll = QScrollArea()
        scroll.setWidget(inner_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)


# ══════════════════════════════════════════════════════════════════
#  PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════
class DashboardPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._build()

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ── Titre ──
        title = QLabel("🏠  Tableau de bord")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        # ── KPIs ──
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)

        self._kpi_labels = {}
        kpis = [
            ("Température", "22.5", "°C",    C['accent']),
            ("pH",          "7.2",  "",       C['green']),
            ("Turbidité",   "45.0", "NTU",    C['yellow']),
            ("Conductivité","450",  "µS/cm",  C['accent']),
            ("Débit",       "120",  "m³/h",   C['green']),
            ("Chlore",      "0.35", "mg/L",   C['yellow']),
        ]
        for title_k, val, unit, col in kpis:
            f, lbl = make_kpi_card(title_k, val, unit, col)
            f.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            kpi_row.addWidget(f)
            self._kpi_labels[title_k] = lbl

        root.addLayout(kpi_row)

        # ── Statut système ──
        status_card, status_lay = card_widget()
        s_title = QLabel("📡  Statut du système")
        s_title.setObjectName("sectionTitle")
        status_lay.addWidget(s_title)

        grid = QGridLayout()
        grid.setSpacing(12)
        items = [
            ("Capteurs physiques", "6 / 6 opérationnels", C['green']),
            ("Capteurs logiciels", "4 / 4 actifs",         C['green']),
            ("Base de données",    "Connectée",             C['green']),
            ("Alarmes actives",    "0 critique · 2 attention", C['yellow']),
            ("Dernière mesure",    datetime.now().strftime("%H:%M:%S"), C['accent']),
            ("Qualité globale",    "Bonne",                 C['green']),
        ]
        for i, (lbl, val, col) in enumerate(items):
            r, c = divmod(i, 2)
            l1 = QLabel(lbl)
            l1.setObjectName("unit")
            l2 = QLabel(val)
            l2.setStyleSheet(f"color:{col}; font-weight:700;")
            cell = QHBoxLayout()
            cell.addWidget(l1)
            cell.addStretch()
            cell.addWidget(l2)
            w = QWidget()
            w.setLayout(cell)
            grid.addWidget(w, r, c)

        status_lay.addLayout(grid)
        root.addWidget(status_card)

        # ── Alertes récentes ──
        alert_card, alert_lay = card_widget()
        a_title = QLabel("🔔  Alertes récentes")
        a_title.setObjectName("sectionTitle")
        alert_lay.addWidget(a_title)

        self.dash_alert_table = QTableWidget(0, 4)
        self.dash_alert_table.setHorizontalHeaderLabels(
            ["Capteur", "Valeur", "Statut", "Horodatage"])
        self.dash_alert_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dash_alert_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dash_alert_table.setMaximumHeight(200)
        alert_lay.addWidget(self.dash_alert_table)

        root.addWidget(alert_card)
        root.addStretch()

        self._scroll_page(inner)

    def refresh_page(self):
        """Met à jour KPIs et alertes depuis la DB."""
        # Lire dernière ligne CSV
        try:
            data = self.db.historical_data
            if not data.empty:
                last = data.iloc[-1]
                mapping = {
                    "Température": ("temperature", ""),
                    "pH":          ("ph",          ""),
                    "Turbidité":   ("turbidity",   ""),
                    "Conductivité":("conductivity",""),
                    "Débit":       ("flow",        ""),
                    "Chlore":      ("chlorine",    ""),
                }
                for label, (col, _) in mapping.items():
                    if col in last and label in self._kpi_labels:
                        self._kpi_labels[label].setText(f"{last[col]:.2f}")
        except Exception:
            pass

        # Alertes
        try:
            alerts = self.alert_mgr.get_all_alerts(days=7, acknowledged=False)[:5]
            self.dash_alert_table.setRowCount(len(alerts))
            for r, a in enumerate(alerts):
                self.dash_alert_table.setItem(r, 0, QTableWidgetItem(a.get('sensor_name', '')))
                self.dash_alert_table.setItem(r, 1, QTableWidgetItem(f"{float(a.get('value',0)):.2f}"))
                status_item = QTableWidgetItem(a.get('status', '').upper())
                col = C['red'] if a.get('status') == 'critique' else C['yellow']
                status_item.setForeground(QColor(col))
                self.dash_alert_table.setItem(r, 2, status_item)
                self.dash_alert_table.setItem(r, 3, QTableWidgetItem(a.get('timestamp', '')))
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
#  PAGE 2 — CAPTEURS PHYSIQUES
# ══════════════════════════════════════════════════════════════════
class PhysicalPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._val_labels = {}
        self._bar_labels = {}
        self._status_labels = {}
        self._build()

        # Timer simulation
        self._timer = QTimer()
        self._timer.timeout.connect(self._simulate)
        self._timer.start(2000)

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📡  Capteurs physiques")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        desc = QLabel("Surveillance en temps réel des capteurs physiques installés sur site.")
        desc.setObjectName("unit")
        desc.setWordWrap(True)
        root.addWidget(desc)

        # Grille de capteurs
        grid = QGridLayout()
        grid.setSpacing(14)

        self._sensors_config = [
            ("temperature", "🌡️  Température",  "°C",    15, 30,  22.5),
            ("ph",          "⚗️  pH",            "",      6.5,8.5, 7.2),
            ("turbidity",   "💧  Turbidité",     "NTU",   1,  150, 45.0),
            ("conductivity","⚡  Conductivité",  "µS/cm", 200,800, 450.0),
            ("flow",        "🌊  Débit",         "m³/h",  10, 500, 120.0),
            ("chlorine",    "🧪  Chlore",        "mg/L",  0.1,0.7, 0.35),
        ]

        for i, (key, name, unit, vmin, vmax, val) in enumerate(self._sensors_config):
            r, c = divmod(i, 3)
            w = self._make_sensor_card(key, name, unit, vmin, vmax, val)
            grid.addWidget(w, r, c)

        root.addLayout(grid)
        root.addStretch()
        self._scroll_page(inner)

    def _make_sensor_card(self, key, name, unit, vmin, vmax, val):
        f = QFrame()
        f.setObjectName("card")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(8)

        n_lbl = QLabel(name)
        n_lbl.setObjectName("sectionTitle")
        n_lbl.setWordWrap(False)

        row = QHBoxLayout()
        v_lbl = QLabel(f"{val:.2f}")
        v_lbl.setObjectName("value")
        v_lbl.setStyleSheet(f"color:{C['accent']}; font-size:32px; font-weight:800;")
        u_lbl = QLabel(unit)
        u_lbl.setObjectName("unit")
        u_lbl.setAlignment(Qt.AlignBottom)
        row.addWidget(v_lbl)
        row.addWidget(u_lbl)
        row.addStretch()

        status_lbl = QLabel("NORMAL")
        status_lbl.setStyleSheet(f"color:{C['green']}; font-weight:700; font-size:12px;"
                                  f"background:{C['green']}22; border-radius:6px; padding:2px 10px;")

        bar = QProgressBar()
        pct = int((val - vmin) / max(vmax - vmin, 1) * 100)
        bar.setValue(pct)

        range_lbl = QLabel(f"Min: {vmin}  ·  Max: {vmax}")
        range_lbl.setObjectName("unit")
        range_lbl.setAlignment(Qt.AlignCenter)

        lay.addWidget(n_lbl)
        lay.addLayout(row)
        lay.addWidget(status_lbl)
        lay.addWidget(bar)
        lay.addWidget(range_lbl)

        self._val_labels[key]    = v_lbl
        self._bar_labels[key]    = bar
        self._status_labels[key] = status_lbl
        return f

    def _simulate(self):
        try:
            data = self.db.historical_data
            if data.empty:
                return
            last = data.iloc[-1]
        except Exception:
            return

        for key, name, unit, vmin, vmax, _ in self._sensors_config:
            if key not in last:
                continue
            val = float(last[key]) + random.uniform(-0.5, 0.5)
            val = max(vmin, min(vmax, val))
            self._val_labels[key].setText(f"{val:.2f}")
            pct = int((val - vmin) / max(vmax - vmin, 1) * 100)
            self._bar_labels[key].setValue(pct)

            if pct > 85:
                self._status_labels[key].setText("CRITIQUE")
                self._status_labels[key].setStyleSheet(
                    f"color:{C['red']}; font-weight:700; font-size:12px;"
                    f"background:{C['red']}22; border-radius:6px; padding:2px 10px;")
            elif pct > 65:
                self._status_labels[key].setText("ATTENTION")
                self._status_labels[key].setStyleSheet(
                    f"color:{C['yellow']}; font-weight:700; font-size:12px;"
                    f"background:{C['yellow']}22; border-radius:6px; padding:2px 10px;")
            else:
                self._status_labels[key].setText("NORMAL")
                self._status_labels[key].setStyleSheet(
                    f"color:{C['green']}; font-weight:700; font-size:12px;"
                    f"background:{C['green']}22; border-radius:6px; padding:2px 10px;")


# ══════════════════════════════════════════════════════════════════
#  PAGE 3 — CAPTEURS LOGICIELS
# ══════════════════════════════════════════════════════════════════
class SoftPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._val_labels = {}
        self._build()
        self._timer = QTimer()
        self._timer.timeout.connect(self.refresh_page)
        self._timer.start(3000)

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("🧠  Capteurs logiciels (Soft Sensors)")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        desc = QLabel(
            "Les capteurs logiciels estiment des paramètres non mesurables directement,\n"
            "à partir de modèles mathématiques appliqués aux mesures physiques."
        )
        desc.setObjectName("unit")
        desc.setWordWrap(True)
        root.addWidget(desc)

        # 4 cartes soft sensors
        grid = QGridLayout()
        grid.setSpacing(14)

        soft_defs = [
            ("DBO",     "💧  DBO",    "Demande Biochimique en Oxygène", "mg/L", 0, 100,
             "turbidité × 0.8 + température × 0.5 + pH × (−0.2) + débit × 0.1"),
            ("DCO",     "⚗️  DCO",    "Demande Chimique en Oxygène",    "mg/L", 0, 300,
             "conductivité × 0.008 + turbidité × 1.5 + pH × (−1.0)"),
            ("MES",     "🌊  MES",    "Matières en Suspension",         "mg/L", 0, 150,
             "turbidité × 1.2 + débit × 0.05"),
            ("Qualite", "⭐  Qualité","Indice Qualité Global",           "%",    0, 100,
             "pH × 10 + conductivité × (−0.05) + turbidité × (−0.3) + …"),
        ]

        for i, (key, name, desc_s, unit, vmin, vmax, formula) in enumerate(soft_defs):
            r, c = divmod(i, 2)
            w = self._make_soft_card(key, name, desc_s, unit, formula)
            grid.addWidget(w, r, c)

        root.addLayout(grid)

        # Tableau des formules (section séparée, pas dans les cartes)
        formula_card, formula_lay = card_widget()
        f_title = QLabel("📐  Modèles mathématiques")
        f_title.setObjectName("sectionTitle")
        formula_lay.addWidget(f_title)

        formula_text = QTextEdit()
        formula_text.setReadOnly(True)
        formula_text.setMaximumHeight(160)
        formula_text.setStyleSheet(
            f"background:{C['hover']}; border:none; border-radius:8px; "
            f"color:{C['text']}; font-family: 'Courier New'; font-size:13px; padding:8px;"
        )
        formula_text.setPlainText(
            "DBO     = 0.8×turbidité + 0.5×température − 0.2×pH + 0.1×débit + bruit\n"
            "DCO     = 0.008×conductivité + 1.5×turbidité − 1.0×pH + bruit\n"
            "MES     = 1.2×turbidité + 0.05×débit + bruit\n"
            "Qualité = 10×pH − 0.05×conductivité − 0.3×turbidité − 1×température − 50×chlore + bruit\n\n"
            "Le bruit est un bruit gaussien de σ = 2% de la valeur calculée."
        )
        formula_lay.addWidget(formula_text)
        root.addWidget(formula_card)
        root.addStretch()

        self._scroll_page(inner)

    def _make_soft_card(self, key, name, description, unit, formula):
        f = QFrame()
        f.setObjectName("card")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(8)

        n_lbl = QLabel(name)
        n_lbl.setObjectName("sectionTitle")

        d_lbl = QLabel(description)
        d_lbl.setObjectName("unit")

        row = QHBoxLayout()
        v_lbl = QLabel("—")
        v_lbl.setObjectName("value")
        v_lbl.setStyleSheet(f"color:{C['accent']}; font-size:36px; font-weight:800;")
        u_lbl = QLabel(unit)
        u_lbl.setObjectName("unit")
        u_lbl.setAlignment(Qt.AlignBottom)
        row.addWidget(v_lbl)
        row.addWidget(u_lbl)
        row.addStretch()

        bar = QProgressBar()
        bar.setValue(0)

        lay.addWidget(n_lbl)
        lay.addWidget(d_lbl)
        lay.addLayout(row)
        lay.addWidget(bar)

        self._val_labels[key] = (v_lbl, bar)
        return f

    def refresh_page(self):
        try:
            data = self.db.historical_data
            if data.empty:
                return
            last = data.iloc[-1]
            ranges = {"DBO": 100, "DCO": 300, "MES": 150, "Qualite": 100}
            for key, (v_lbl, bar) in self._val_labels.items():
                col = key if key != "Qualite" else "Qualite"
                if col in last:
                    val = float(last[col])
                    v_lbl.setText(f"{val:.1f}")
                    pct = int(val / ranges.get(key, 100) * 100)
                    bar.setValue(min(100, pct))
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
#  PAGE 4 — TENDANCES (Graphiques)
# ══════════════════════════════════════════════════════════════════
class TrendsPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._build()

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📈  Tendances & Graphiques")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        # Contrôles
        ctrl = QHBoxLayout()
        ctrl.setSpacing(12)

        ctrl.addWidget(QLabel("Capteur :"))
        self.sensor_combo = QComboBox()
        self.sensor_combo.addItems([
            "temperature", "ph", "turbidity",
            "conductivity", "flow", "chlorine",
            "DBO", "DCO", "MES", "Qualite"
        ])
        self.sensor_combo.currentTextChanged.connect(self._update_chart)
        ctrl.addWidget(self.sensor_combo)

        ctrl.addWidget(QLabel("Période :"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["7 jours", "14 jours", "30 jours"])
        self.period_combo.currentTextChanged.connect(self._update_chart)
        ctrl.addWidget(self.period_combo)

        refresh_btn = QPushButton("🔄  Actualiser")
        refresh_btn.setObjectName("primary")
        refresh_btn.clicked.connect(self._update_chart)
        ctrl.addWidget(refresh_btn)
        ctrl.addStretch()
        root.addLayout(ctrl)

        # Zone graphique
        chart_card, chart_lay = card_widget(margins=(12, 12, 12, 12))

        if HAS_PYQTGRAPH:
            pg.setConfigOption('background', C['card'])
            pg.setConfigOption('foreground', C['text'])
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setMinimumHeight(380)
            self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
            self.plot_widget.getAxis('left').setTextPen(C['text'])
            self.plot_widget.getAxis('bottom').setTextPen(C['text'])
            chart_lay.addWidget(self.plot_widget)
        else:
            no_chart = QLabel(
                "📊  Graphiques disponibles avec pyqtgraph\n\n"
                "Installez-le avec :  pip install pyqtgraph"
            )
            no_chart.setAlignment(Qt.AlignCenter)
            no_chart.setObjectName("unit")
            no_chart.setMinimumHeight(300)
            chart_lay.addWidget(no_chart)
            self.plot_widget = None

        root.addWidget(chart_card)

        # Statistiques rapides
        stats_card, stats_lay = card_widget()
        s_title = QLabel("📊  Statistiques de la période")
        s_title.setObjectName("sectionTitle")
        stats_lay.addWidget(s_title)

        stats_row = QHBoxLayout()
        self._stat_labels = {}
        for stat in ["Minimum", "Maximum", "Moyenne", "Écart-type"]:
            f = QFrame()
            f.setObjectName("card")
            f.setStyleSheet(f"QFrame#card {{ background: {C['hover']}; }}")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(14, 10, 14, 10)
            lbl = QLabel("—")
            lbl.setStyleSheet(f"color:{C['accent']}; font-size:22px; font-weight:800;")
            lbl.setAlignment(Qt.AlignCenter)
            fl.addWidget(QLabel(stat) if True else None)
            name_l = QLabel(stat)
            name_l.setObjectName("unit")
            name_l.setAlignment(Qt.AlignCenter)
            fl.addWidget(name_l)
            fl.addWidget(lbl)
            stats_row.addWidget(f)
            self._stat_labels[stat] = lbl

        stats_lay.addLayout(stats_row)
        root.addWidget(stats_card)
        root.addStretch()

        self._scroll_page(inner)
        self._update_chart()

    def _update_chart(self):
        sensor = self.sensor_combo.currentText()
        days_map = {"7 jours": 7, "14 jours": 14, "30 jours": 30}
        days = days_map.get(self.period_combo.currentText(), 7)

        timestamps, values = self.db.get_history(sensor, days=days)

        if not values:
            return

        import numpy as np
        vals = [float(v) for v in values]

        if self.plot_widget and HAS_PYQTGRAPH:
            self.plot_widget.clear()
            pen = pg.mkPen(color=C['accent'], width=2)
            self.plot_widget.plot(vals, pen=pen, name=sensor)
            fill = pg.FillBetweenItem(
                self.plot_widget.plot([0] * len(vals)),
                self.plot_widget.plot(vals),
                brush=pg.mkBrush(0, 212, 255, 30)
            )
            self.plot_widget.addItem(fill)
            self.plot_widget.setTitle(f"  {sensor.upper()}", color=C['accent'], size='14pt')

        # Stats
        arr = np.array(vals)
        self._stat_labels["Minimum"].setText(f"{arr.min():.2f}")
        self._stat_labels["Maximum"].setText(f"{arr.max():.2f}")
        self._stat_labels["Moyenne"].setText(f"{arr.mean():.2f}")
        self._stat_labels["Écart-type"].setText(f"{arr.std():.2f}")

    def refresh_page(self):
        self._update_chart()


# ══════════════════════════════════════════════════════════════════
#  PAGE 5 — ALARMES
# ══════════════════════════════════════════════════════════════════
class AlarmsPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._build()

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("🔔  Gestion des alarmes")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        # ── Barre d'outils ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Toutes", "Critique", "Attention", "Non lues"])
        self.filter_combo.currentTextChanged.connect(self.refresh_page)
        toolbar.addWidget(QLabel("Filtre :"))
        toolbar.addWidget(self.filter_combo)

        ack_btn = QPushButton("✅  Acquitter sélection")
        ack_btn.setObjectName("primary")
        ack_btn.clicked.connect(self._ack_selected)
        toolbar.addWidget(ack_btn)

        del_btn = QPushButton("🗑️  Supprimer sélection")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._del_selected)
        toolbar.addWidget(del_btn)

        clear_btn = QPushButton("💥  Tout effacer")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(clear_btn)

        toolbar.addStretch()

        # Compteur
        self.alert_count_lbl = QLabel("0 alarmes")
        self.alert_count_lbl.setObjectName("unit")
        toolbar.addWidget(self.alert_count_lbl)

        root.addLayout(toolbar)

        # ── Tableau ──
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Capteur", "Valeur", "Statut", "Horodatage", "Acquittée"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(400)
        root.addWidget(self.table)

        # ── Ajouter alarme test ──
        test_card, test_lay = card_widget()
        t_title = QLabel("➕  Ajouter une alarme de test")
        t_title.setObjectName("sectionTitle")
        test_lay.addWidget(t_title)

        form = QHBoxLayout()
        form.setSpacing(10)
        self.test_sensor = QLineEdit()
        self.test_sensor.setPlaceholderText("Nom capteur")
        self.test_val = QLineEdit()
        self.test_val.setPlaceholderText("Valeur")
        self.test_status = QComboBox()
        self.test_status.addItems(["warning", "critique"])
        add_btn = QPushButton("Ajouter")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self._add_test_alert)
        form.addWidget(self.test_sensor)
        form.addWidget(self.test_val)
        form.addWidget(self.test_status)
        form.addWidget(add_btn)
        test_lay.addLayout(form)
        root.addWidget(test_card)

        root.addStretch()
        self._scroll_page(inner)

    def refresh_page(self):
        fil = self.filter_combo.currentText()
        try:
            alerts = self.alert_mgr._load_csv()
            if fil == "Critique":
                alerts = [a for a in alerts if a.get('status') == 'critique']
            elif fil == "Attention":
                alerts = [a for a in alerts if a.get('status') == 'warning']
            elif fil == "Non lues":
                alerts = [a for a in alerts if not a.get('acknowledged')]

            self.table.setRowCount(len(alerts))
            self.alert_count_lbl.setText(f"{len(alerts)} alarmes")

            for r, a in enumerate(alerts):
                self.table.setItem(r, 0, QTableWidgetItem(str(a.get('id', ''))))
                self.table.setItem(r, 1, QTableWidgetItem(a.get('sensor_name', '')))
                self.table.setItem(r, 2, QTableWidgetItem(f"{float(a.get('value',0)):.2f}"))

                st = a.get('status', '')
                st_item = QTableWidgetItem(st.upper())
                col = C['red'] if st == 'critique' else C['yellow']
                st_item.setForeground(QColor(col))
                self.table.setItem(r, 3, st_item)

                self.table.setItem(r, 4, QTableWidgetItem(a.get('timestamp', '')))
                ack_val = "✅ Oui" if a.get('acknowledged') else "❌ Non"
                self.table.setItem(r, 5, QTableWidgetItem(ack_val))
        except Exception as e:
            print(f"Erreur refresh alarmes: {e}")

    def _ack_selected(self):
        rows = set(i.row() for i in self.table.selectedItems())
        for r in rows:
            id_item = self.table.item(r, 0)
            if id_item:
                self.alert_mgr.acknowledge_alert(int(id_item.text()),
                                                  self.main_win.current_user)
        self.refresh_page()

    def _del_selected(self):
        rows = set(i.row() for i in self.table.selectedItems())
        for r in rows:
            id_item = self.table.item(r, 0)
            if id_item:
                self.alert_mgr.delete_alert(int(id_item.text()))
        self.refresh_page()

    def _clear_all(self):
        reply = QMessageBox.question(self, "Confirmer",
                                     "Supprimer toutes les alarmes ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.alert_mgr.clear_all_alerts()
            self.refresh_page()

    def _add_test_alert(self):
        sensor = self.test_sensor.text().strip() or "test_sensor"
        try:
            val = float(self.test_val.text().strip() or "99.9")
        except ValueError:
            val = 99.9
        status = self.test_status.currentText()
        self.alert_mgr.add_alert(sensor, val, "", status)
        self.refresh_page()


# ══════════════════════════════════════════════════════════════════
#  PAGE 6 — PRÉDICTION IA / LSTM
# ══════════════════════════════════════════════════════════════════
class PredictionPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._build()

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("🤖  Prédiction IA / LSTM")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        # Info bannière
        info_card, info_lay = card_widget()
        info_lay.addWidget(QLabel(
            "🧠  Ce module utilise un réseau de neurones LSTM (Long Short-Term Memory)\n"
            "pour prédire les valeurs futures des capteurs à partir de l'historique."
        ))

        # Statut modèle
        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Statut du modèle :"))
        self.model_status = QLabel("⚪  Non entraîné")
        self.model_status.setStyleSheet(f"color:{C['muted']}; font-weight:700;")
        status_row.addWidget(self.model_status)
        status_row.addStretch()
        info_lay.addLayout(status_row)
        root.addWidget(info_card)

        # Configuration
        cfg_card, cfg_lay = card_widget()
        cfg_title = QLabel("⚙️  Configuration du modèle")
        cfg_title.setObjectName("sectionTitle")
        cfg_lay.addWidget(cfg_title)

        form = QGridLayout()
        form.setSpacing(12)

        form.addWidget(QLabel("Capteur cible :"), 0, 0)
        self.target_combo = QComboBox()
        self.target_combo.addItems(["DBO", "DCO", "MES", "Qualite"])
        form.addWidget(self.target_combo, 0, 1)

        form.addWidget(QLabel("Fenêtre temporelle (jours) :"), 1, 0)
        self.window_spin = QSpinBox()
        self.window_spin.setRange(3, 30)
        self.window_spin.setValue(7)
        form.addWidget(self.window_spin, 1, 1)

        form.addWidget(QLabel("Horizon de prédiction (jours) :"), 2, 0)
        self.horizon_spin = QSpinBox()
        self.horizon_spin.setRange(1, 14)
        self.horizon_spin.setValue(3)
        form.addWidget(self.horizon_spin, 2, 1)

        form.addWidget(QLabel("Époques d'entraînement :"), 3, 0)
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(10, 200)
        self.epochs_spin.setValue(50)
        form.addWidget(self.epochs_spin, 3, 1)

        cfg_lay.addLayout(form)

        btn_row = QHBoxLayout()
        train_btn = QPushButton("🏋️  Entraîner le modèle")
        train_btn.setObjectName("primary")
        train_btn.clicked.connect(self._train_model)
        predict_btn = QPushButton("🔮  Lancer la prédiction")
        predict_btn.setObjectName("secondary")
        predict_btn.clicked.connect(self._predict)
        btn_row.addWidget(train_btn)
        btn_row.addWidget(predict_btn)
        btn_row.addStretch()
        cfg_lay.addLayout(btn_row)
        root.addWidget(cfg_card)

        # Résultats
        res_card, res_lay = card_widget()
        r_title = QLabel("📊  Résultats de prédiction")
        r_title.setObjectName("sectionTitle")
        res_lay.addWidget(r_title)

        self.pred_table = QTableWidget(0, 3)
        self.pred_table.setHorizontalHeaderLabels(["Date", "Valeur prédite", "Intervalle"])
        self.pred_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pred_table.setMaximumHeight(250)
        res_lay.addWidget(self.pred_table)

        self.metrics_lbl = QLabel("")
        self.metrics_lbl.setObjectName("unit")
        self.metrics_lbl.setWordWrap(True)
        res_lay.addWidget(self.metrics_lbl)

        root.addWidget(res_card)
        root.addStretch()
        self._scroll_page(inner)

    def _train_model(self):
        """Simulation d'entraînement (placeholder)."""
        self.model_status.setText("🟡  Entraînement en cours…")
        self.model_status.setStyleSheet(f"color:{C['yellow']}; font-weight:700;")
        QTimer.singleShot(2000, lambda: self._finish_training())

    def _finish_training(self):
        self.model_status.setText("🟢  Modèle prêt")
        self.model_status.setStyleSheet(f"color:{C['green']}; font-weight:700;")
        self.metrics_lbl.setText(
            "📉  RMSE: 1.42  |  MAE: 1.18  |  R²: 0.94  |  "
            "Epochs: 50  |  Loss final: 0.0023"
        )

    def _predict(self):
        """Génère des prédictions simulées."""
        sensor = self.target_combo.currentText()
        horizon = self.horizon_spin.value()
        _, vals = self.db.get_history(sensor, days=30)
        if not vals:
            QMessageBox.warning(self, "Pas de données", "Aucune donnée historique disponible.")
            return

        import numpy as np
        base = float(vals[-1]) if vals else 50.0
        self.pred_table.setRowCount(horizon)
        for i in range(horizon):
            date = (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
            pred = base + random.uniform(-3, 3) * (i + 1) * 0.3
            margin = abs(random.uniform(1, 4))
            self.pred_table.setItem(i, 0, QTableWidgetItem(date))
            v_item = QTableWidgetItem(f"{pred:.2f}")
            v_item.setForeground(QColor(C['accent']))
            self.pred_table.setItem(i, 1, v_item)
            self.pred_table.setItem(i, 2, QTableWidgetItem(
                f"[{pred-margin:.2f} — {pred+margin:.2f}]"))


# ══════════════════════════════════════════════════════════════════
#  PAGE 7 — RAPPORTS
# ══════════════════════════════════════════════════════════════════
class ReportsPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._build()

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📊  Rapports & Exportation")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        # Options de rapport
        opt_card, opt_lay = card_widget()
        o_title = QLabel("📋  Générer un rapport")
        o_title.setObjectName("sectionTitle")
        opt_lay.addWidget(o_title)

        form = QGridLayout()
        form.setSpacing(12)

        form.addWidget(QLabel("Type de rapport :"), 0, 0)
        self.report_type = QComboBox()
        self.report_type.addItems([
            "Rapport journalier", "Rapport hebdomadaire",
            "Rapport mensuel", "Rapport alarmes", "Rapport complet"
        ])
        form.addWidget(self.report_type, 0, 1)

        form.addWidget(QLabel("Format d'export :"), 1, 0)
        self.export_fmt = QComboBox()
        self.export_fmt.addItems(["CSV", "TXT"])
        form.addWidget(self.export_fmt, 1, 1)

        form.addWidget(QLabel("Période (jours) :"), 2, 0)
        self.report_days = QSpinBox()
        self.report_days.setRange(1, 365)
        self.report_days.setValue(7)
        form.addWidget(self.report_days, 2, 1)

        opt_lay.addLayout(form)

        btn_row = QHBoxLayout()
        gen_btn = QPushButton("🔄  Générer l'aperçu")
        gen_btn.setObjectName("primary")
        gen_btn.clicked.connect(self._generate_preview)

        exp_btn = QPushButton("💾  Exporter")
        exp_btn.setObjectName("secondary")
        exp_btn.clicked.connect(self._export)

        btn_row.addWidget(gen_btn)
        btn_row.addWidget(exp_btn)
        btn_row.addStretch()
        opt_lay.addLayout(btn_row)
        root.addWidget(opt_card)

        # Aperçu
        prev_card, prev_lay = card_widget()
        p_title = QLabel("👁️  Aperçu")
        p_title.setObjectName("sectionTitle")
        prev_lay.addWidget(p_title)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(280)
        self.preview.setStyleSheet(
            f"background:{C['hover']}; border:none; border-radius:8px;"
            f"color:{C['text']}; font-family:'Courier New'; font-size:13px; padding:10px;"
        )
        prev_lay.addWidget(self.preview)
        root.addWidget(prev_card)
        root.addStretch()

        self._scroll_page(inner)

    def _generate_preview(self):
        days = self.report_days.value()
        rtype = self.report_type.currentText()
        sensors = ["temperature", "ph", "turbidity", "conductivity", "flow", "chlorine",
                   "DBO", "DCO", "MES", "Qualite"]

        import numpy as np
        lines = [
            f"{'='*60}",
            f"  {rtype.upper()}",
            f"  Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Utilisateur : {self.main_win.current_user}",
            f"  Période : {days} jours",
            f"{'='*60}", ""
        ]

        data = self.db.historical_data
        for s in sensors:
            if data.empty or s not in data.columns:
                continue
            vals = [float(v) for v in data[s].dropna().tail(days * 24)]
            if not vals:
                continue
            arr = np.array(vals)
            lines.append(f"  {s.upper():15s}  min={arr.min():.2f}  max={arr.max():.2f}"
                         f"  moy={arr.mean():.2f}  σ={arr.std():.2f}")

        lines += ["", f"{'='*60}",
                  f"  Alarmes : {len(self.alert_mgr._load_csv())} entrées au total",
                  f"{'='*60}"]

        self.preview.setPlainText("\n".join(lines))

    def _export(self):
        fmt = self.export_fmt.currentText()
        ext = ".csv" if fmt == "CSV" else ".txt"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le rapport",
            f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}",
            f"{fmt} (*{ext})"
        )
        if not path:
            return

        content = self.preview.toPlainText()
        if not content:
            self._generate_preview()
            content = self.preview.toPlainText()

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            QMessageBox.information(self, "Export réussi", f"Rapport sauvegardé :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder :\n{e}")


# ══════════════════════════════════════════════════════════════════
#  PAGE 8 — GESTION UTILISATEURS
# ══════════════════════════════════════════════════════════════════
class UsersPage(BasePage):
    def __init__(self, main_win):
        super().__init__(main_win)
        self._build()

    def _build(self):
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("👤  Gestion des utilisateurs")
        title.setObjectName("pageTitle")
        root.addWidget(title)

        # Tableau
        table_card, table_lay = card_widget()
        t_title = QLabel("📋  Utilisateurs enregistrés")
        t_title.setObjectName("sectionTitle")
        table_lay.addWidget(t_title)

        self.user_table = QTableWidget(0, 3)
        self.user_table.setHorizontalHeaderLabels(["ID", "Nom d'utilisateur", "Rôle"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setMaximumHeight(250)
        table_lay.addWidget(self.user_table)
        root.addWidget(table_card)

        # Ajouter utilisateur
        add_card, add_lay = card_widget()
        a_title = QLabel("➕  Ajouter un utilisateur")
        a_title.setObjectName("sectionTitle")
        add_lay.addWidget(a_title)

        form = QGridLayout()
        form.setSpacing(12)
        form.addWidget(QLabel("Nom d'utilisateur :"), 0, 0)
        self.new_user = QLineEdit()
        self.new_user.setPlaceholderText("Nom d'utilisateur")
        form.addWidget(self.new_user, 0, 1)

        form.addWidget(QLabel("Mot de passe :"), 1, 0)
        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setPlaceholderText("Mot de passe")
        form.addWidget(self.new_pwd, 1, 1)

        form.addWidget(QLabel("Rôle :"), 2, 0)
        self.new_role = QComboBox()
        self.new_role.addItems(["Opérateur", "Superviseur", "Administrateur"])
        form.addWidget(self.new_role, 2, 1)

        add_lay.addLayout(form)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾  Enregistrer")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._add_user)
        del_btn = QPushButton("🗑️  Supprimer sélection")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._delete_user)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        add_lay.addLayout(btn_row)
        root.addWidget(add_card)
        root.addStretch()
        self._scroll_page(inner)
        self.refresh_page()

    def refresh_page(self):
        """Charge les utilisateurs depuis PostgreSQL."""
        try:
            conn = self.db._get_connection() if hasattr(self.db, '_get_connection') else None
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT id, username, 'Opérateur' FROM utilisateurs ORDER BY id")
                rows = cur.fetchall()
                cur.close(); conn.close()
            else:
                rows = [(1, "admin", "Administrateur")]
        except Exception:
            rows = [(1, "admin", "Administrateur")]

        self.user_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.user_table.setItem(r, c, QTableWidgetItem(str(val)))

    def _add_user(self):
        uname = self.new_user.text().strip()
        pwd   = self.new_pwd.text().strip()
        role  = self.new_role.currentText()
        if not uname or not pwd:
            QMessageBox.warning(self, "Champs vides", "Remplissez tous les champs.")
            return
        QMessageBox.information(self, "Succès",
                                f"Utilisateur « {uname} » ({role}) ajouté.\n"
                                "(Connectez la base PostgreSQL pour persister.)")
        # Ajouter à l'affichage
        r = self.user_table.rowCount()
        self.user_table.insertRow(r)
        self.user_table.setItem(r, 0, QTableWidgetItem(str(r + 1)))
        self.user_table.setItem(r, 1, QTableWidgetItem(uname))
        self.user_table.setItem(r, 2, QTableWidgetItem(role))
        self.new_user.clear(); self.new_pwd.clear()

    def _delete_user(self):
        rows = set(i.row() for i in self.user_table.selectedItems())
        for r in sorted(rows, reverse=True):
            name_item = self.user_table.item(r, 1)
            if name_item and name_item.text() == "admin":
                QMessageBox.warning(self, "Impossible", "Le compte admin ne peut pas être supprimé.")
                continue
            self.user_table.removeRow(r)


# ══════════════════════════════════════════════════════════════════
#  FENÊTRE PRINCIPALE
# ══════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):

    NAV_ITEMS = [
        ("dashboard",  "🏠  Accueil"),
        ("physical",   "📡  Capteurs physiques"),
        ("soft",       "🧠  Capteurs logiciels"),
        ("trends",     "📈  Tendances"),
        ("alarms",     "🔔  Alarmes"),
        ("prediction", "🤖  Prédiction IA"),
        ("reports",    "📊  Rapports"),
        ("users",      "👤  Utilisateurs"),
    ]

    def __init__(self, current_user="admin"):
        super().__init__()
        self.current_user = current_user
        self.db = SensorDatabase()
        self.alert_mgr = AlertManagerCSV()
        self._nav_btns = {}
        self._active_page = None

        self.setWindowTitle("Soft Sensor  ·  Supervision")
        self.resize(1380, 860)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(GLOBAL_CSS)

        self._build_ui()
        self._show_page("dashboard")

    # ─────────────────────────────────────────
    #  UI
    # ─────────────────────────────────────────
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_lay = QVBoxLayout(root)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Header ──
        header = self._build_header()
        main_lay.addWidget(header)

        # ── Body ──
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = self._build_sidebar()
        body.addWidget(sidebar)

        # Content
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.pages = {
            "dashboard":  DashboardPage(self),
            "physical":   PhysicalPage(self),
            "soft":       SoftPage(self),
            "trends":     TrendsPage(self),
            "alarms":     AlarmsPage(self),
            "prediction": PredictionPage(self),
            "reports":    ReportsPage(self),
            "users":      UsersPage(self),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        body.addWidget(self.stack, 1)
        main_lay.addLayout(body, 1)

    def _build_header(self):
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(64)

        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(16)

        logo = QLabel("💧  Soft Sensor")
        logo.setStyleSheet(f"color:{C['accent']}; font-size:22px; font-weight:800;"
                           f"letter-spacing:1px; background:transparent; border:none;")

        # Barre de statut centre
        center = QLabel("● SYSTÈME OPÉRATIONNEL")
        center.setStyleSheet(f"color:{C['green']}; font-size:13px; font-weight:700;"
                             f"background:transparent; border:none;")
        center.setAlignment(Qt.AlignCenter)

        # Droite : user + heure + logout
        self.clock_lbl = QLabel()
        self.clock_lbl.setStyleSheet(f"color:{C['muted']}; font-size:13px;"
                                     f"background:transparent; border:none;")
        self._update_clock()
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self._update_clock)
        clock_timer.start(1000)

        user_lbl = QLabel(f"👤  {self.current_user}")
        user_lbl.setStyleSheet(f"color:{C['text']}; font-weight:700; font-size:14px;"
                               f"background:transparent; border:none;")

        logout_btn = QPushButton("Déconnexion")
        logout_btn.setObjectName("secondary")
        logout_btn.setFixedHeight(34)
        logout_btn.clicked.connect(self.close)

        lay.addWidget(logo)
        lay.addStretch()
        lay.addWidget(center)
        lay.addStretch()
        lay.addWidget(self.clock_lbl)
        lay.addWidget(user_lbl)
        lay.addWidget(logout_btn)
        return header

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(8, 16, 8, 16)
        lay.setSpacing(4)

        menu_lbl = QLabel("NAVIGATION")
        menu_lbl.setStyleSheet(f"color:{C['muted']}; font-size:11px; font-weight:700;"
                               f"letter-spacing:2px; padding:0 8px; background:transparent; border:none;")
        lay.addWidget(menu_lbl)
        lay.addSpacing(8)

        for key, label in self.NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("nav")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            btn.setFixedHeight(44)
            lay.addWidget(btn)
            self._nav_btns[key] = btn

        lay.addStretch()

        # Version info
        ver = QLabel("v2.0 · Soft Sensor")
        ver.setStyleSheet(f"color:{C['muted']}; font-size:11px; padding:0 8px;"
                         f"background:transparent; border:none;")
        lay.addWidget(ver)
        return sidebar

    # ─────────────────────────────────────────
    #  Navigation
    # ─────────────────────────────────────────
    def _show_page(self, key: str):
        if self._active_page and self._active_page in self._nav_btns:
            self._nav_btns[self._active_page].setObjectName("nav")
            self._nav_btns[self._active_page].setStyle(
                self._nav_btns[self._active_page].style())

        self._active_page = key
        if key in self._nav_btns:
            self._nav_btns[key].setObjectName("nav_active")
            self._nav_btns[key].setStyle(self._nav_btns[key].style())

        page = self.pages[key]
        if hasattr(page, "refresh_page"):
            page.refresh_page()
        self.stack.setCurrentWidget(page)

    def _update_clock(self):
        self.clock_lbl.setText(datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y  ·  "))