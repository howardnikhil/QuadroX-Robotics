from setuptools import find_packages, setup
from glob import glob
import os

package_name = "quadrox_control"
setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "description/urdf"), glob("description/urdf/*")),
        (os.path.join("share", package_name, "description/rviz"), glob("description/rviz/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="QuadroX Robotics Contributors",
    maintainer_email="maintainers@example.com",
    description="Simulation-first quadruped robot control foundation",
    license="MIT",
    tests_require=["pytest"],
    entry_points={"console_scripts": [
        "gait_controller = quadrox_control.gait_controller:main",
        "safety_supervisor = quadrox_control.safety_supervisor:main",
    ]},
)
