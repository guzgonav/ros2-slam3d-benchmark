import os

from ament_index_python.packages import get_package_share_directory
import launch
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    param_file = os.path.join(
        get_package_share_directory('slam_benchmarks'),
        'config', 'lidarslam', 'lidarslam.yaml'
    )

    rviz_param_dir = launch.substitutions.LaunchConfiguration(
        'rviz_param_dir',
        default=os.path.join(
            get_package_share_directory('lidarslam'),
            'rviz',
            'mapping.rviz'
        )
    )

    return LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            'rviz_param_dir',
            default_value=rviz_param_dir,
            description='Full path to the rviz config file'
        ),

        # Remap LiDAR frame: base_link -> hesai (Hesai Pandar frame)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['--x', '0.0', '--y', '0.0', '--z', '0.124',
                       '--qx', '0.0', '--qy', '0.0', '--qz', '1.0', '--qw', '0.0',
                       '--frame-id', 'base_link', '--child-frame-id', 'pandar']
        ),

        # Scan matching (front-end SLAM)
        Node(
            package='scanmatcher',
            executable='scanmatcher_node',
            name='scan_matcher',
            output='screen',
            parameters=[param_file],
            remappings=[
                ('/input_cloud', '/hesai/pandar'),
                ('/imu', '/alphasense_driver_ros/imu'),
            ],
        ),

        # Graph-based SLAM (back-end, loop closure)
        Node(
            package='graph_based_slam',
            executable='graph_based_slam_node',
            name='graph_based_slam',
            output='screen',
            parameters=[param_file],
        ),

        # Visualization
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_param_dir]
        ),
    ])
