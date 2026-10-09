from __future__ import annotations
import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from .gait import GaitGenerator
from .joint_model import JOINT_NAMES

class GaitController(Node):
    """Publish desired quadruped joint positions for stand or trot mode."""
    def __init__(self):
        super().__init__("quadrox_gait_controller")
        self.declare_parameter("publish_rate_hz", 50.0)
        self.declare_parameter("gait_mode", "stand")
        self.declare_parameter("gait_frequency_hz", 1.0)
        self.declare_parameter("hip_amplitude_rad", 0.18)
        self.declare_parameter("upper_amplitude_rad", 0.22)
        self.declare_parameter("lower_amplitude_rad", 0.28)
        self.declare_parameter("neutral_upper_rad", 0.55)
        self.declare_parameter("neutral_lower_rad", -1.1)
        self.declare_parameter("output_topic", "/quadrox/desired_joint_states")
        self.rate_hz = float(self.get_parameter("publish_rate_hz").value)
        if not math.isfinite(self.rate_hz) or self.rate_hz <= 0:
            raise ValueError("publish_rate_hz must be finite and positive")
        self.mode = str(self.get_parameter("gait_mode").value).lower()
        self.gait = GaitGenerator(
            frequency_hz=float(self.get_parameter("gait_frequency_hz").value),
            hip_amplitude_rad=float(self.get_parameter("hip_amplitude_rad").value),
            upper_amplitude_rad=float(self.get_parameter("upper_amplitude_rad").value),
            lower_amplitude_rad=float(self.get_parameter("lower_amplitude_rad").value),
            neutral_upper_rad=float(self.get_parameter("neutral_upper_rad").value),
            neutral_lower_rad=float(self.get_parameter("neutral_lower_rad").value))
        topic = str(self.get_parameter("output_topic").value)
        self.publisher = self.create_publisher(JointState, topic, 10)
        self.start_time = time.monotonic()
        self.timer = self.create_timer(1.0 / self.rate_hz, self.publish_pose)
        self.get_logger().info(f"Gait controller mode={self.mode}, rate={self.rate_hz} Hz")

    def publish_pose(self):
        try:
            pose = self.gait.pose(time.monotonic() - self.start_time, self.mode)
        except ValueError as exc:
            self.get_logger().error(str(exc))
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [float(pose[name]) for name in JOINT_NAMES]
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = GaitController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
