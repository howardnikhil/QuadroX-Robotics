# Architecture

## Nodes

- `quadrox_gait_controller`: publishes `sensor_msgs/msg/JointState` on `/quadrox/desired_joint_states`. `stand` emits a fixed neutral pose; `trot` emits a periodic joint-space approximation with diagonal phase pairs. This is not a model-based or dynamically stable gait.
- `quadrox_safety_supervisor`: subscribes to desired states and `/quadrox/estop`; rejects unknown/duplicate joints, missing values, non-finite values, and out-of-range positions. It publishes a neutral pose while disabled, stopped, or when commands become stale. E-stop is latched for the lifetime of the node.

## Hardware boundary

`/quadrox/safe_joint_states` is still a software command topic and must not directly drive real motors. A hardware adapter must enforce actuator-side limits, communication watchdogs, and publish measured state. See the official [ros2_control documentation](https://control.ros.org/jazzy/doc/getting_started/getting_started.html).

## Current limitations

No inverse kinematics, body attitude stabilization, foot contact sensing, terrain estimation, motor driver, encoder implementation, validated physical model, or safety certification.
