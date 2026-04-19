import os
import random
import pandas as pd
from datetime import datetime, timedelta
from core.soft_sensor import SoftSensor


class SensorDatabase:
    def __init__(self, filename="sensors_data.csv"):
        self.filename = filename
        self.physical_sensors = {}
        self.soft_sensors = {}
        self.historical_data = pd.DataFrame()
        self.init_default_sensors()
        self.create_initial_history()

    def init_default_sensors(self):
        self.physical_sensors = {
            "temperature": {"name": "Température", "unit": "°C", "min": 15, "max": 30, "value": 22.5},
            "ph": {"name": "pH", "unit": "", "min": 6.5, "max": 8.5, "value": 7.2},
            "turbidity": {"name": "Turbidité", "unit": "NTU", "min": 1, "max": 150, "value": 45.0},
            "conductivity": {"name": "Conductivité", "unit": "µS/cm", "min": 200, "max": 800, "value": 450.0},
            "flow": {"name": "Débit", "unit": "m³/h", "min": 10, "max": 500, "value": 120.0},
            "chlorine": {"name": "Chlore", "unit": "mg/L", "min": 0.1, "max": 0.7, "value": 0.35}
        }

        self.soft_sensors = {
            "DBO": SoftSensor("DBO", "Demande Biochimique", "mg/L",
                              ["turbidity", "temperature", "ph", "flow"],
                              [0.8, 0.5, -0.2, 0.1], 0, 100),
            "DCO": SoftSensor("DCO", "Demande Chimique", "mg/L",
                              ["conductivity", "turbidity", "ph"],
                              [0.008, 1.5, -1.0], 0, 300),
            "MES": SoftSensor("MES", "Matières en Suspension", "mg/L",
                              ["turbidity", "flow"], [1.2, 0.05], 0, 150),
            "Qualite": SoftSensor("Qualité", "Indice Qualité", "%",
                                  ["ph", "conductivity", "turbidity", "temperature", "chlorine"],
                                  [10, -0.05, -0.3, -1, -50], 0, 100)
        }

        self.load_history()

    def create_initial_history(self):
        if self.historical_data.empty:
            physical = {n: s["value"] for n, s in self.physical_sensors.items()}
            for day in range(30):
                for name in self.physical_sensors:
                    variation = random.uniform(-2, 2)
                    new_val = self.physical_sensors[name]["value"] + variation
                    new_val = max(
                        self.physical_sensors[name]["min"],
                        min(self.physical_sensors[name]["max"], new_val)
                    )
                    self.physical_sensors[name]["value"] = new_val
                    physical[name] = new_val

                soft_vals = {}
                for name, sensor in self.soft_sensors.items():
                    soft_vals[name] = sensor.calculate(physical)

                record = {
                    "timestamp": (datetime.now() - timedelta(days=30 - day)).strftime("%Y-%m-%d %H:%M:%S")
                }
                record.update(physical)
                record.update(soft_vals)

                self.historical_data = pd.concat(
                    [self.historical_data, pd.DataFrame([record])],
                    ignore_index=True
                )

            self.save_history()

    def load_history(self):
        if os.path.exists(self.filename):
            try:
                self.historical_data = pd.read_csv(self.filename)
            except Exception:
                self.historical_data = pd.DataFrame()

    def save_history(self):
        if not self.historical_data.empty:
            self.historical_data.to_csv(self.filename, index=False)

    def save_history_as(self, filename):
        if not self.historical_data.empty:
            self.historical_data.to_csv(filename, index=False)

    def add_measurement(self, physical_values, soft_values):
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **physical_values,
            **soft_values
        }
        self.historical_data = pd.concat(
            [self.historical_data, pd.DataFrame([record])],
            ignore_index=True
        )

        if len(self.historical_data) > 500:
            self.historical_data = self.historical_data.tail(500)

        self.save_history()

    def get_history(self, sensor_name, days=7):
        if self.historical_data.empty:
            return [], []

        cutoff = datetime.now() - timedelta(days=days)
        mask = pd.to_datetime(self.historical_data["timestamp"]) >= cutoff
        data = self.historical_data[mask]

        if sensor_name in data.columns:
            return data["timestamp"].tolist(), data[sensor_name].tolist()

        return [], []