#!/usr/bin/env python3
"""
Save the latest /global_voxel_map to a PCD file.

Usage:
    python3 save_map.py                     # saves on Ctrl+C
    python3 save_map.py -o my_map.pcd       # custom output path
    python3 save_map.py --once              # save first received message and exit
"""

import argparse
import signal
import sys
from pathlib import Path
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
import open3d as o3d


class MapSaver(Node):
    def __init__(self, output_path: str, once: bool):
        super().__init__('map_saver')
        self.output_path = output_path
        self.once = once
        self.latest_points = None

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.create_subscription(PointCloud2, '/global_voxel_map', self._callback, qos)
        self.get_logger().info(
            f"Subscribed to /global_voxel_map. "
            f"{'Will save first message.' if once else 'Press Ctrl+C to save latest map.'}"
        )

    def _callback(self, msg: PointCloud2):
        pts = pc2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True)
        self.latest_points = np.vstack([pts['x'], pts['y'], pts['z']]).T
        self.get_logger().info(f"Received map: {len(self.latest_points)} points.")

        if self.once:
            self.save()
            rclpy.shutdown()

    def save(self):
        if self.latest_points is None or len(self.latest_points) == 0:
            self.get_logger().warn("No map received yet, nothing to save.")
            return
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.latest_points)
        o3d.io.write_point_cloud(self.output_path, pcd)
        print(f"Saved {len(self.latest_points)} points → {self.output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default='map.pcd', help='Output PCD file path')
    parser.add_argument('--once', action='store_true', help='Save first message and exit')
    args, ros_args = parser.parse_known_args()

    rclpy.init(args=ros_args)
    node = MapSaver(output_path=args.output, once=args.once)

    # Handle both Ctrl+C (SIGINT) and launch shutdown (SIGTERM)
    def _shutdown(signum, frame):
        rclpy.shutdown()

    signal.signal(signal.SIGTERM, _shutdown)

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, Exception):
        pass
    finally:
        node.save()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
