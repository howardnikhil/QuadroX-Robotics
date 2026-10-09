from __future__ import annotations
import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool
from .joint_model import JOINT_NAMES, JointLimit, neutral_pose, validate_joint_command

class SafetySupervisor(Node):
    """Validate joint targets and gate output on enable, E-stop and freshness."""
    def __init__(self):
        super().__init__("quadrox_safety_supervisor")
        self.declare_parameter("input_topic", "/quadrox/desired_joint_states")
        self.declare_parameter("output_topic", "/quadrox/safe_joint_states")
        self.declare_parameter("estop_topic", "/quadrox/estop")
        self.declare_parameter("enabled_at_start", False)
        self.declare_parameter("command_timeout_sec", 0.25)
        self.declare_parameter("joint_limits", [-1.5, 1.5])
        self.declare_parameter("neutral_upper_rad", 0.55)
        self.declare_parameter("neutral_lower_rad", -1.1)
        self.timeout = float(self.get_parameter("command_timeout_sec").value)
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError("command_timeout_sec must be finite and positive")
        limits = list(self.get_parameter("joint_limits").value)
        if len(limits) != 2:
            raise ValueError("joint_limits must be [min, max]")
        self.limits = {name: JointLimit(float(limits[0]), float(limits[1])) for name in JOINT_NAMES}
        self.neutral = neutral_pose(0.0, float(self.get_parameter("neutral_upper_rad").value),
                                    float(self.get_parameter("neutral_lower_rad").value))
        self.enabled = bool(self.get_parameter("enabled_at_start").value)
        self.estop_latched = False
        self.last_command_walltime = 0.0
        self.last_command = None
        self.last_timeout_warning = 0.0
        self.output = self.create_publisher(JointState, str(self.get_parameter("output_topic").value), 10)
        self.create_subscription(JointState, str(self.get_parameter("input_topic").value), self.command_callback, 10)
        self.create_subscription(Bool, str(self.get_parameter("estop_topic").value), self.estop_callback, 10)
        self.create_timer(0.02, self.publish_safe_command)
        self.get_logger().warning("Starts DISABLED by default. Software gate is not a certified safety controller.")

    def estop_callback(self, msg):
        if msg.data:
            self.estop_latched = True
            self.enabled = False
            self.get_logger().error("E-stop latched; restart node to clear software latch.")

    def command_callback(self, msg):
        valid, reason = validate_joint_command(msg.name, msg.position, self.limits)
        if not valid:
            self.get_logger().warning(f"Rejected command: {reason}")
            return
        self.last_command = msg
        self.last_command_walltime = time.monotonic()

    def safe_message(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [self.neutral[name] for name in JOINT_NAMES]
        return msg

    def publish_safe_command(self):
        fresh = self.last_command is not None and time.monotonic() - self.last_command_walltime <= self.timeout
        if self.enabled and not self.estop_latched and fresh:
            out = JointState()
            out.header.stamp = self.get_clock().now().to_msg()
            out.name = list(self.last_command.name)
            out.position = list(self.last_command.position)
            self.output.publish(out)
        else:
            if self.enabled and not fresh and time.monotonic() - self.last_timeout_warning > 2.0:
                self.get_logger().warning("Command timeout: disabling and publishing neutral pose")
                self.last_timeout_warning = time.monotonic()
                self.enabled = False
            self.output.publish(self.safe_message())

def main(args=None):
    rclpy.init(args=args)
    node = SafetySupervisor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
