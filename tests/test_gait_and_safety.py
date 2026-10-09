import math
import pytest
from quadrox_control.gait import GaitGenerator
from quadrox_control.joint_model import JOINT_NAMES, JointLimit, neutral_pose, validate_joint_command

def test_neutral_pose_has_all_twelve_joints():
    pose = neutral_pose()
    assert len(pose) == 12
    assert set(pose) == set(JOINT_NAMES)

def test_stand_pose_is_constant():
    gait = GaitGenerator()
    assert gait.pose(0.0, "stand") == gait.pose(4.2, "stand")

def test_trot_pose_has_finite_values_and_all_joints():
    pose = GaitGenerator().pose(0.2, "trot")
    assert set(pose) == set(JOINT_NAMES)
    assert all(math.isfinite(v) for v in pose.values())

def test_unknown_mode_rejected():
    with pytest.raises(ValueError):
        GaitGenerator().pose(0.0, "gallop")

def test_non_finite_time_rejected():
    with pytest.raises(ValueError):
        GaitGenerator().pose(float("nan"), "trot")

def test_valid_command_passes():
    limits = {name: JointLimit(-2.0, 2.0) for name in JOINT_NAMES}
    pose = neutral_pose()
    ok, reason = validate_joint_command(list(pose), list(pose.values()), limits)
    assert ok, reason

def test_out_of_limit_command_fails():
    limits = {name: JointLimit(-1.0, 1.0) for name in JOINT_NAMES}
    pose = neutral_pose()
    ok, reason = validate_joint_command(list(pose), list(pose.values()), limits)
    assert not ok
    assert "out of limits" in reason

def test_duplicate_joint_name_fails():
    limits = {name: JointLimit(-2.0, 2.0) for name in JOINT_NAMES}
    ok, reason = validate_joint_command(["front_left_hip_joint"] * 2, [0.0, 0.0], limits)
    assert not ok
    assert "duplicate" in reason

def test_non_finite_position_fails():
    limits = {name: JointLimit(-2.0, 2.0) for name in JOINT_NAMES}
    ok, reason = validate_joint_command(["front_left_hip_joint"], [float("inf")], limits)
    assert not ok
    assert "non-finite" in reason
