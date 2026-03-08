# lidarslam

Graph-based 3D LiDAR SLAM using NDT scan matching (front-end) and pose graph optimization with loop closure (back-end).

**Source:** [rsasaki0109/lidarslam_ros2](https://github.com/rsasaki0109/lidarslam_ros2)

## Architecture

Two nodes run together:

| Node | Package | Role |
|---|---|---|
| `scanmatcher_node` | `scanmatcher` | Front-end: NDT scan matching, odometry |
| `graph_based_slam_node` | `graph_based_slam` | Back-end: pose graph, loop closure |

## Build

```bash
source /opt/ros/jazzy/setup.bash
colcon build --packages-select lidarslam lidarslam_msgs scanmatcher graph_based_slam slam_benchmarks
source install/setup.bash
```

## Configuration

Config file: [`src/slam_benchmarks/config/lidarslam/lidarslam.yaml`](../src/slam_benchmarks/config/lidarslam/lidarslam.yaml)

Key parameters:

| Parameter | Value | Description |
|---|---|---|
| `registration_method` | `NDT` | Scan matching method (NDT or GICP) |
| `ndt_resolution` | `2.0` | NDT voxel size (m) |
| `use_imu` | `false` | IMU integration |
| `use_odom` | `false` | Wheel odometry |
| `trans_for_mapupdate` | `1.5` | Min translation (m) before map update |

## Oxford Spires Dataset

### Sensor setup

| Sensor | Topic | Frame |
|---|---|---|
| Hesai Pandar QT64 | `/hesai/pandar` | `pandar` |
| Alphasense IMU | `/alphasense_driver_ros/imu` | — |

### Calibrated TF (base_link → pandar)

```
translation: x=0.0, y=0.0, z=0.124 m
rotation: qx=0.0, qy=0.0, qz=1.0, qw=0.0  (180° around Z — upside-down mount)
```

### Launch

```bash
ros2 launch slam_benchmarks lidarslam.launch.py
```

### Bag playback

The Hesai topic uses `best_effort` reliability — create a QoS override file:

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

Suggested displays:
- `PointCloud2` → `/map`
- `Path` → `/path`
- `TF`