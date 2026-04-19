# core/alert_manager.py
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class AlertManagerCSV:
    """
    Gestionnaire d'alertes basé sur un fichier CSV.
    Stocke, lit, met à jour et supprime les alertes capteurs.
    """

    HEADERS = ["id", "sensor_name", "value", "unit", "status",
               "timestamp", "acknowledged", "user_ack"]

    # Seuils par capteur : (min_critique, max_critique, min_warning, max_warning)
    THRESHOLDS = {
        "temperature":  {"warning": (18, 28),  "critique": (15, 30)},
        "ph":           {"warning": (6.8, 8.2), "critique": (6.5, 8.5)},
        "turbidity":    {"warning": (50, 100),  "critique": (100, 150)},
        "conductivity": {"warning": (300, 700), "critique": (200, 800)},
        "flow":         {"warning": (20, 400),  "critique": (10, 500)},
        "chlorine":     {"warning": (0.2, 0.6), "critique": (0.1, 0.7)},
        "DBO":          {"warning": (40, 70),   "critique": (70, 100)},
        "DCO":          {"warning": (80, 200),  "critique": (200, 300)},
        "MES":          {"warning": (50, 100),  "critique": (100, 150)},
        "Qualite":      {"warning": (20, 40),   "critique": (0, 20)},
    }

    def __init__(self, filename: str = "alerts_history.csv"):
        self.filepath = Path("data") / filename
        self.filepath.parent.mkdir(exist_ok=True)

        # Mapping pour conversion bool CSV → Python
        self._bool_map = {
            'True': True, 'true': True, '1': True,
            'False': False, 'false': False, '0': False, '': False
        }

    # ──────────────────────────────────────────────────
    #  I/O CSV (privé)
    # ──────────────────────────────────────────────────

    def _load_csv(self) -> List[Dict[str, Any]]:
        """Charge toutes les alertes depuis le fichier CSV."""
        if not self.filepath.exists():
            return []

        alerts = []
        try:
            with open(self.filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['id']           = int(row['id']) if str(row.get('id', '')).isdigit() else 0
                    row['value']        = float(row.get('value', 0))
                    row['acknowledged'] = self._bool_map.get(str(row.get('acknowledged', 'false')), False)
                    alerts.append(row)
        except Exception as e:
            print(f"[AlertManager] Erreur lecture CSV : {e}")
        return alerts

    def _save_csv(self, alerts: List[Dict[str, Any]]) -> None:
        """Sauvegarde la liste d'alertes dans le fichier CSV."""
        try:
            with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.HEADERS)
                writer.writeheader()
                for alert in alerts:
                    row = alert.copy()
                    row['acknowledged'] = str(row['acknowledged']).lower()
                    # Garantir que toutes les colonnes sont présentes
                    for h in self.HEADERS:
                        row.setdefault(h, '')
                    writer.writerow({h: row[h] for h in self.HEADERS})
        except Exception as e:
            print(f"[AlertManager] Erreur sauvegarde CSV : {e}")

    # ──────────────────────────────────────────────────
    #  CRUD Alertes
    # ──────────────────────────────────────────────────

    def add_alert(self,
                  sensor_name: str,
                  value: float,
                  unit: str = "",
                  status: str = "warning") -> int:
        """
        Ajoute une nouvelle alerte et retourne son ID.
        status : 'warning' | 'critique'
        """
        alerts = self._load_csv()
        new_id = max((a['id'] for a in alerts), default=0) + 1

        alert = {
            "id":           new_id,
            "sensor_name":  sensor_name,
            "value":        value,
            "unit":         unit,
            "status":       status,
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "acknowledged": False,
            "user_ack":     ""
        }
        alerts.append(alert)
        self._save_csv(alerts)
        print(f"[AlertManager] ➕ Alerte #{new_id} : {sensor_name} = {value} {unit} ({status})")
        return new_id

    def check_and_alert(self,
                        sensor_name: str,
                        value: float,
                        unit: str = "") -> str | None:
        """
        Vérifie la valeur d'un capteur par rapport aux seuils définis.
        Crée automatiquement une alerte si nécessaire.
        Retourne le statut déclenché ('critique', 'warning') ou None.
        """
        thresholds = self.THRESHOLDS.get(sensor_name)
        if not thresholds:
            return None

        w_min, w_max = thresholds["warning"]
        c_min, c_max = thresholds["critique"]

        if value < c_min or value > c_max:
            self.add_alert(sensor_name, value, unit, "critique")
            return "critique"
        elif value < w_min or value > w_max:
            self.add_alert(sensor_name, value, unit, "warning")
            return "warning"
        return None

    def get_all_alerts(self,
                       days: int = 30,
                       acknowledged: bool | None = None) -> List[Dict[str, Any]]:
        """
        Retourne les alertes filtrées.

        Args:
            days:         Nombre de jours à inclure (depuis maintenant).
            acknowledged: True → alertes lues, False → non lues, None → toutes.
        """
        all_alerts = self._load_csv()
        cutoff = datetime.now() - timedelta(days=days)

        result = []
        for a in all_alerts:
            try:
                ts = datetime.strptime(a['timestamp'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            if ts < cutoff:
                continue
            if acknowledged is not None and a['acknowledged'] != acknowledged:
                continue
            result.append(a)

        return sorted(result, key=lambda x: x['timestamp'], reverse=True)

    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retourne toutes les alertes d'un statut donné ('warning' ou 'critique')."""
        return [a for a in self._load_csv() if a.get('status') == status]

    def acknowledge_alert(self, alert_id: int, user: str = "") -> bool:
        """Marque une alerte comme lue par l'utilisateur donné."""
        alerts = self._load_csv()
        for a in alerts:
            if a['id'] == alert_id:
                a['acknowledged'] = True
                a['user_ack']     = user
                self._save_csv(alerts)
                print(f"[AlertManager] ✅ Alerte #{alert_id} acquittée par '{user}'")
                return True
        print(f"[AlertManager] ⚠️  Alerte #{alert_id} introuvable")
        return False

    def acknowledge_all(self, user: str = "") -> int:
        """Acquitte toutes les alertes non lues. Retourne le nombre acquitté."""
        alerts = self._load_csv()
        count = 0
        for a in alerts:
            if not a['acknowledged']:
                a['acknowledged'] = True
                a['user_ack']     = user
                count += 1
        self._save_csv(alerts)
        print(f"[AlertManager] ✅ {count} alertes acquittées par '{user}'")
        return count

    def delete_alert(self, alert_id: int) -> bool:
        """Supprime une alerte par son ID. Retourne True si supprimée."""
        alerts = self._load_csv()
        filtered = [a for a in alerts if a['id'] != alert_id]
        if len(filtered) < len(alerts):
            self._save_csv(filtered)
            print(f"[AlertManager] 🗑️  Alerte #{alert_id} supprimée")
            return True
        print(f"[AlertManager] ⚠️  Alerte #{alert_id} introuvable")
        return False

    def purge_old_alerts(self, days: int = 30) -> int:
        """
        Supprime les alertes de plus de `days` jours.
        Retourne le nombre d'alertes supprimées.
        """
        all_alerts  = self._load_csv()
        cutoff      = datetime.now() - timedelta(days=days)
        recent      = []
        deleted     = 0

        for a in all_alerts:
            try:
                ts = datetime.strptime(a['timestamp'], "%Y-%m-%d %H:%M:%S")
                if ts >= cutoff:
                    recent.append(a)
                else:
                    deleted += 1
            except ValueError:
                deleted += 1  # Ligne corrompue → supprimée

        self._save_csv(recent)
        print(f"[AlertManager] 🧹 {deleted} alertes purgées (> {days}j)")
        return deleted

    def clear_all_alerts(self) -> bool:
        """Supprime toutes les alertes du fichier CSV."""
        self._save_csv([])
        print("[AlertManager] 💥 Toutes les alertes ont été supprimées")
        return True

    # ──────────────────────────────────────────────────
    #  Statistiques
    # ──────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, int]:
        """
        Retourne un dictionnaire de statistiques sur les alertes.

        Clés retournées :
            total    — nombre total d'alertes
            critique — alertes de statut 'critique'
            warning  — alertes de statut 'warning'
            unread   — alertes non acquittées
            today    — alertes créées aujourd'hui
        """
        alerts  = self._load_csv()
        today   = datetime.now().strftime("%Y-%m-%d")

        return {
            "total":    len(alerts),
            "critique": sum(1 for a in alerts if a.get('status') == 'critique'),
            "warning":  sum(1 for a in alerts if a.get('status') == 'warning'),
            "unread":   sum(1 for a in alerts if not a.get('acknowledged')),
            "today":    sum(1 for a in alerts if str(a.get('timestamp', '')).startswith(today)),
        }

    def get_sensor_stats(self, sensor_name: str) -> Dict[str, Any]:
        """Statistiques filtrées pour un capteur spécifique."""
        alerts = [a for a in self._load_csv() if a.get('sensor_name') == sensor_name]
        values = [a['value'] for a in alerts]
        return {
            "count":    len(alerts),
            "critique": sum(1 for a in alerts if a.get('status') == 'critique'),
            "warning":  sum(1 for a in alerts if a.get('status') == 'warning'),
            "min_val":  min(values) if values else None,
            "max_val":  max(values) if values else None,
            "avg_val":  sum(values) / len(values) if values else None,
        }

    # ──────────────────────────────────────────────────
    #  Utilitaires
    # ──────────────────────────────────────────────────

    def count(self) -> int:
        """Nombre total d'alertes dans le fichier."""
        return len(self._load_csv())

    def exists(self, alert_id: int) -> bool:
        """Vérifie si une alerte avec cet ID existe."""
        return any(a['id'] == alert_id for a in self._load_csv())

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (f"<AlertManagerCSV fichier='{self.filepath}' "
                f"total={stats['total']} non_lues={stats['unread']}>")