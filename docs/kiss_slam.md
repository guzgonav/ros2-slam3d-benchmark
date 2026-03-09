# KISS-SLAM

Simple, robust 3D LiDAR SLAM using KISS-ICP for odometry (front-end) and map-closure-based loop detection with pose graph optimization (back-end). Purely LiDAR-based — no IMU.

**Source:** [abwerby/kiss-slam-ros2](https://github.com/abwerby/kiss-slam-ros2) — ROS2 wrapper of [PRBonn/kiss-slam](https://github.com/PRBonn/kiss-slam)

## Architecture

Two nodes run together:

| Node | Package | Role |
|---|---|---|
| `odometry_node` | `kiss_slam_ros` | Front-end: KISS-ICP point cloud registration, deskewing, `odom → base_link` TF |
| `slam_node` | `kiss_slam_ros` | Back-end: local map graph, loop closure, pose graph optimization, `map → odom` TF |

## Build

`kiss_slam` Python library (C++ pybind11 extension) must be installed first:

```bash
sudo apt install libeigen3-dev libsuitesparse-dev
pip install kiss-slam --break-system-packages
```

Then build the ROS2 wrapper:

```bash
# Add COLCON_IGNORE so colcon skips the pybind11 CMake target at repo root
touch src/kiss-slam-ros2/COLCON_IGNORE

# Symlink the ROS2 package directly into src/ so colcon finds it
ln -s kiss-slam-ros2/ros2/src/kiss_slam_ros src/kiss_slam_ros

colcon build --symlink-install --packages-select kiss_slam_ros slam_benchmarks
source install/setup.bash
```

## Configuration

| File | Node | Purpose |
|---|---|---|
| [`src/slam_benchmarks/config/kiss_slam/odometry_params.yaml`](../src/slam_benchmarks/config/kiss_slam/odometry_params.yaml) | `odometry_node` | KISS-ICP front-end parameters |
| [`src/slam_benchmarks/config/kiss_slam/slam_params.yaml`](../src/slam_benchmarks/config/kiss_slam/slam_params.yaml) | `slam_node` | Back-end parameters |

Key parameters:

| Parameter | Value | Description |
|---|---|---|
| `kiss_slam.odometry.preprocessing.max_range` | `200.0` | Hesai QT64 max range (m) |
| `kiss_slam.odometry.preprocessing.min_range` | `0.5` | Exclude points closer than 0.5 m |
| `kiss_slam.odometry.preprocessing.deskew` | `true` | Motion undistortion |
| `kiss_slam.local_mapper.voxel_size` | `0.2` | Local map voxel resolution (m) |
| `kiss_slam.local_mapper.splitting_distance` | `5.0` | Distance (m) before creating a new local map |
| `kiss_slam.loop_closer.overlap_threshold` | `0.4` | Min overlap ratio to accept a loop closure |

## Oxford Spires Dataset

### Sensor setup

| Sensor | Topic | Frame |
|---|---|---|
| Hesai Pandar QT64 | `/hesai/pandar` | `pandar` |

> No IMU — KISS-SLAM is purely LiDAR-based.

### Calibrated TF (base_link → pandar)

```
translation: x=0.0, y=0.0, z=0.124 m
rotation: qx=0.0, qy=0.0, qz=1.0, qw=0.0  (180° around Z — upside-down mount)
```

### Launch

```bash
# Default (with RViz)
ros2 launch slam_benchmarks kiss_slam.launch.py

# Without RViz
ros2 launch slam_benchmarks kiss_slam.launch.py visualize:=false

# Save map on shutdown
ros2 launch slam_benchmarks kiss_slam.launch.py save_map:=true

# Save map to custom path
ros2 launch slam_benchmarks kiss_slam.launch.py save_map:=true map_output:=/path/to/map.pcd
```

### Bag playback

```bash
cat > /tmp/qos_override.yaml << 'EOF'
/hesai/pandar:
  reliability: best_effort
  history: keep_last
  depth: 10
EOF

ros2 bag play /path/to/bag.db3 --clock \
  --qos-profile-overrides-path /tmp/qos_override.yaml
```

### RViz

Fixed frame: `map`

> The `map` frame only appears in TF once the `slam_node` processes its first keyframe (a moment after bag playback starts). Use `base_link` as fixed frame to verify data is flowing before SLAM initialises.

| Display | Topic | Notes |
|---|---|---|
| `PointCloud2` | `/global_voxel_map` | Accumulated global map — published after each local map split (~5 m) |
| `PointCloud2` | `/deskewed_points` | Current deskewed scan |
| `Pose` | `/global_pose` | SLAM-corrected robot pose in `map` frame |
| `Odometry` | `/odometry` | Raw KISS-ICP odometry |
| `TF` | — | `map → odom → base_link` chain |

### Saving the map

The map is saved automatically on shutdown when `save_map:=true` is passed to the launch file. Default output: `maps/kiss_slam/map.pcd` (relative to workspace root).

To save manually while SLAM is running:

```bash
python3 src/slam_benchmarks/scripts/save_map.py -o maps/kiss_slam/map.pcd
# Press Ctrl+C when done — saves the latest received map
```

Visualize the saved file:

```bash
pcl_viewer maps/kiss_slam/map.pcd
```
