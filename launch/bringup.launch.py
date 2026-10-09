from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    share = get_package_share_directory("quadrox_control")
    params = os.path.join(share, "config", "quadrox.yaml")
    return LaunchDescription([
        Node(package="quadrox_control", executable="gait_controller",
             name="quadrox_gait_controller", output="screen", parameters=[params]),
        Node(package="quadrox_control", executable="safety_supervisor",
             name="quadrox_safety_supervisor", output="screen", parameters=[params]),
    ])
