from setuptools import find_packages, setup

package_name = "fusion_ros"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages",
            ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="you",
    maintainer_email="you@example.com",
    description="ROS 2 node wrapping fusion_lab for live LiDAR+camera fusion.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "fusion_node = fusion_ros.fusion_node:main",
        ],
    },
)
