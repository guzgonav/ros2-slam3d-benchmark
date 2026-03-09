import os

from ament_index_python.packages import get_package_share_directory, get_package_prefix

# Workspace root: install/slam_benchmarks → install → workspace
_ws_root = os.path.dirname(os.path.dirname(get_package_prefix('slam_benchmarks')))
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    config_dir = os.path.join(
        get_package_share_directory('slam_benchmarks'),
        'config', 'kiss_slam'
    )

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    visualize = LaunchConfiguration('visualize', default='true')
    save_map = LaunchConfiguration('save_map', default='false')
    map_output = LaunchConfiguration('map_output', default=os.path.join(_ws_root, 'maps', 'kiss_slam', 'map.pcd'))

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use simulation clock (set true when playing bags)'
        ),
        DeclareLaunchArgument(
            'visualize', default_value='true',
            description='Launch RViz2 for visualization'
        ),
        DeclareLaunchArgument(
            'save_map', default_value='false',
            description='Save the map to a PCD file on shutdown'
        ),
        DeclareLaunchArgument(
            'map_output', default_value=os.path.join(_ws_root, 'maps', 'kiss_slam', 'map.pcd'),
            description='Output path for the saved PCD map (relative to cwd or absolute)'
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

        # KISS-SLAM odometry (KISS-ICP front-end)
        Node(
            package='kiss_slam_ros',
            executable='odometry_node',
            name='odometry_node',
            output='screen',
            remappings=[
                ('/points_raw', '/hesai/pandar'),
            ],
            parameters=[
                os.path.join(config_dir, 'odometry_params.yaml'),
                {'use_sim_time': use_sim_time},
            ],
        ),

        # KISS-SLAM back-end (loop closure + pose graph)
        Node(
            package='kiss_slam_ros',
            executable='slam_node',
            name='slam_node',
            output='screen',
            parameters=[
                os.path.join(config_dir, 'slam_params.yaml'),
                {'use_sim_time': use_sim_time},
            ],
        ),

        # Map saver (optional) - saves latest /global_voxel_map to PCD on shutdown
        ExecuteProcess(
            cmd=[
                'python3',
                PathJoinSubstitution(
                    [FindPackageShare('slam_benchmarks'), 'scripts', 'save_map.py']
                ),
                '-o', map_output,
            ],
            output='screen',
            condition=IfCondition(save_map),
        ),

        # Visualization (optional)
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=[
                '-d',
                PathJoinSubstitution(
                    [FindPackageShare('slam_benchmarks'), 'rviz', 'kiss_slam.rviz']
                ),
            ],
            condition=IfCondition(visualize),
        ),
    ])
