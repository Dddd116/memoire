import numpy as np
from datetime import datetime


class SoftSensor:
    def __init__(self, name, description, unit, physical_inputs, coefficients, min_val=0, max_val=100):
        self.name = name
        self.description = description
        self.unit = unit
        self.physical_inputs = physical_inputs
        self.coefficients = coefficients
        self.min_val = min_val
        self.max_val = max_val
        self.current_value = 0
        self.history = []
        self.history_timestamps = []

    def calculate(self, physical_values):
        value = 0

        for i, input_name in enumerate(self.physical_inputs):
            if input_name in physical_values:
                value += self.coefficients[i] * physical_values[input_name]

        if abs(value) > 0:
            value += np.random.normal(0, abs(value) * 0.02)
        else:
            value += np.random.normal(0, 0.1)

        value = max(self.min_val, min(self.max_val, value))
        self.current_value = value

        self.history.append(value)
        self.history_timestamps.append(datetime.now())

        if len(self.history) > 100:
            self.history.pop(0)
            self.history_timestamps.pop(0)

        return value

    def get_status(self):
        if self.current_value > self.max_val * 0.8:
            return "critique"
        elif self.current_value > self.max_val * 0.6:
            return "attention"
        return "normal"