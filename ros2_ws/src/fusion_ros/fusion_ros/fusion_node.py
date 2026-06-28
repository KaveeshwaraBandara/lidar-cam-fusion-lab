"""
fusion_node.py — Phase 7 stub: live LiDAR+camera fusion as a ROS 2 node.

This is intentionally a SKELETON. It subscribes to a camera image topic and a
PointCloud2 topic, runs the same fusion_lab pipeline, and publishes annotated
results. Wire up the real Go2 topic names and extrinsics when you get there.

Build:  cd ros2_ws && colcon build && source install/setup.bash
Run:    ros2 run fusion_ros fusion_node
"""
from __future__ import annotations

import numpy as np
import rclpy
from rclpy.node import Node

# These imports assume fusion_lab is on PYTHONPATH (the Docker image sets that).
try:
    from fusion_lab import YoloDetector, frustum_association
    from fusion_lab.calibration import Calibration
except ImportError:  # keep the node importable even if core pkg isn't built yet
    YoloDetector = None


class FusionNode(Node):
    def __init__(self) -> None:
        super().__init__("fusion_node")

        # --- Parameters (override via ros2 launch / --ros-args) -------------
        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("cloud_topic", "/lidar/points")
        self.declare_parameter("calib_path", "")

        image_topic = self.get_parameter("image_topic").value
        cloud_topic = self.get_parameter("cloud_topic").value

        self.get_logger().info(
            f"FusionNode subscribing to image={image_topic} cloud={cloud_topic}"
        )

        # TODO: import sensor_msgs and message_filters for time-synced pairs.
        # from sensor_msgs.msg import Image, PointCloud2
        # from message_filters import ApproximateTimeSynchronizer, Subscriber
        #
        # self.sync = ApproximateTimeSynchronizer(
        #     [Subscriber(self, Image, image_topic),
        #      Subscriber(self, PointCloud2, cloud_topic)],
        #     queue_size=10, slop=0.1,
        # )
        # self.sync.registerCallback(self.on_pair)

        self.detector = YoloDetector() if YoloDetector else None
        self.calib = None  # load from calib_path when running for real

    def on_pair(self, image_msg, cloud_msg) -> None:
        """Callback for a synchronized (image, cloud) pair.

        Steps (to implement):
          1. cv_bridge: image_msg -> np.ndarray (RGB)
          2. point_cloud2.read_points: cloud_msg -> (N, 3/4) np.ndarray
          3. detections = self.detector.detect(image)
          4. fused = frustum_association(points, detections, self.calib, W, H)
          5. publish MarkerArray (3D boxes) + annotated Image
        """
        raise NotImplementedError("wire up cv_bridge + point_cloud2 here")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
