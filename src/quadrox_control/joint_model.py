"""Pure Python quadruped joint model and validation helpers."""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Mapping, Sequence

LEG_NAMES = ("front_left", "front_right", "rear_left", "rear_right")
JOINT_SUFFIXES = ("hip_joint", "upper_leg_joint", "lower_leg_joint")
JOINT_NAMES = tuple(f"{leg}_{suffix}" for leg in LEG_NAMES for suffix in JOINT_SUFFIXES)

@dataclass(frozen=True)
class JointLimit:
    minimum: float
    maximum: float

    def __post_init__(self):
        if not math.isfinite(self.minimum) or not math.isfinite(self.maximum):
            raise ValueError("Joint limits must be finite")
        if self.minimum >= self.maximum:
            raise ValueError("Joint limit minimum must be below maximum")

def neutral_pose(hip=0.0, upper=0.55, lower=-1.1):
    """Return a neutral joint-space pose; tune angles to the real robot."""
    if not all(math.isfinite(v) for v in (hip, upper, lower)):
        raise ValueError("Neutral pose angles must be finite")
    return {f"{leg}_{suffix}": value for leg in LEG_NAMES
            for suffix, value in zip(JOINT_SUFFIXES, (hip, upper, lower))}

def validate_joint_command(names: Sequence[str], positions: Sequence[float],
                           limits: Mapping[str, JointLimit]):
    """Validate a JointState-style command without depending on ROS."""
    if not names:
        return False, "empty joint names"
    if len(names) != len(positions):
        return False, "joint name/position length mismatch"
    if len(set(names)) != len(names):
        return False, "duplicate joint names"
    for name, value in zip(names, positions):
        if name not in limits:
            return False, f"unknown joint: {name}"
        if not math.isfinite(value):
            return False, f"non-finite position for {name}"
        limit = limits[name]
        if value < limit.minimum or value > limit.maximum:
            return False, f"position out of limits for {name}"
    return True, "ok"
