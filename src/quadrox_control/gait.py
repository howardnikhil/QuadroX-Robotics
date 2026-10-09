"""Deterministic joint-space gait target generator (not a dynamics controller)."""
from __future__ import annotations
import math
from .joint_model import LEG_NAMES, neutral_pose

class GaitGenerator:
    def __init__(self, frequency_hz=1.0, hip_amplitude_rad=0.18,
                 upper_amplitude_rad=0.22, lower_amplitude_rad=0.28,
                 neutral_upper_rad=0.55, neutral_lower_rad=-1.1):
        if frequency_hz <= 0 or not math.isfinite(frequency_hz):
            raise ValueError("frequency_hz must be finite and > 0")
        for value in (hip_amplitude_rad, upper_amplitude_rad, lower_amplitude_rad):
            if not math.isfinite(value) or value < 0:
                raise ValueError("gait amplitudes must be finite and non-negative")
        self.frequency_hz = frequency_hz
        self.hip_amplitude_rad = hip_amplitude_rad
        self.upper_amplitude_rad = upper_amplitude_rad
        self.lower_amplitude_rad = lower_amplitude_rad
        self.neutral_upper_rad = neutral_upper_rad
        self.neutral_lower_rad = neutral_lower_rad
        self._neutral = neutral_pose(0.0, neutral_upper_rad, neutral_lower_rad)

    def pose(self, time_seconds, mode="trot"):
        if not math.isfinite(time_seconds):
            raise ValueError("time_seconds must be finite")
        mode = mode.lower()
        if mode == "stand":
            return dict(self._neutral)
        if mode != "trot":
            raise ValueError(f"Unsupported gait mode: {mode}")
        phase = 2.0 * math.pi * self.frequency_hz * time_seconds
        offsets = {"front_left": 0.0, "rear_right": 0.0,
                   "front_right": math.pi, "rear_left": math.pi}
        result = {}
        for leg in LEG_NAMES:
            p = phase + offsets[leg]
            result[f"{leg}_hip_joint"] = self.hip_amplitude_rad * math.sin(p)
            result[f"{leg}_upper_leg_joint"] = self.neutral_upper_rad + self.upper_amplitude_rad * math.sin(p)
            result[f"{leg}_lower_leg_joint"] = self.neutral_lower_rad + self.lower_amplitude_rad * math.sin(p + math.pi / 3.0)
        return result
