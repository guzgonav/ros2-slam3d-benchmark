import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config_path = os.path.join(
        get_package_share_directory('slam_benchmarks'),
        'config', 'fast_lio'
    )

    fast_lio_launch = os.path.join(
        get_package_share_directory('fast_lio'),
        'launch', 'mapping.launch.py'
    )

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use simulation clock (set true when playing bags)'
        ),

        # Calibrated TF: base_link -> pandar (Hesai QT64, upside-down mount)
        # z=0.124m offset, 180deg rotation around Z axis
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['--x', '0.0', '--y', '0.0', '--z', '0.124',
                       '--qx', '0.0', '--qy', '0.0', '--qz', '1.0', '--qw', '0.0',
                       '--frame-id', 'base_link', '--child-frame-id', 'pandar']
        ),

        # FAST-LIO2 with Oxford Spires config
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(fast_lio_launch),
            launch_arguments={
                'config_path': config_path,
                'config_file': 'oxford_spires.yaml',
                'use_sim_time': use_sim_time,
                'rviz': 'false',
            }.items()
        ),
    ])