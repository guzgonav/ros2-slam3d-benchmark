# FAST-LIO2

Tightly-coupled LiDAR-IMU odometry using an incremental k-d tree (iKD-Tree) for efficient map management.

**Source:** [guzgonav/FAST_LIO](https://github.com/guzgonav/FAST_LIO) — fork of [Ericsii/FAST_LIO_ROS2](https://github.com/Ericsii/FAST_LIO_ROS2)

## Modifications from upstream

- Livox dependency made **optional** via `#ifdef USE_LIVOX` guards + `find_package(livox_ros_driver2 QUIET)` in CMake — builds without Livox if the driver is not found
- Added `hesai_ros::Point` struct in `preprocess.h` for Hesai Pandar QT64 point cloud format
- Fixed `save_to_pcd()` to correctly flatten the full iKD-Tree instead of saving the incomplete publish buffer

## Build

`livox_ros_driver2` must be built first (see [setup.md](setup.md)).

```bash
source /opt/ros/jazzy/setup.bash

# Build Livox driver first
colcon build --packages-select livox_ros_driver2 \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash

# Build FAST-LIO
colcon build --packages-select fast_lio \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

> CMake will print `livox_ros_driver2 found — building with Livox support` or
> `livox_ros_driver2 not found — building without Livox support` depending on whether
> the driver was sourced.

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

### Configuration

Config file: `src/slam_benchmarks/config/fast_lio/oxford_spires.yaml`

Key parameters:

| Parameter | Value | Description |
|---|---|---|
| `lidar_type` | `2` | `2` = standard PointCloud2 (Hesai); `1` = Livox CustomMsg |
| `scan_line` | `64` | Number of LiDAR scan lines |
| `timestamp_unit` | `0` | `0` = seconds |
| `use_imu` | `true` | IMU integration enabled |
| `extrinsic_est_en` | `false` | Extrinsics fixed (pre-calibrated) |

Extrinsics (`T_imu_lidar`) computed as `inv(T_cam0_imu) × T_cam0_lidar` from Oxford Spires calibration files.

### Launch

```bash
ros2 launch fast_lio mapping.launch.py \
  config_file:=oxford_spires.yaml \
  use_sim_time:=true \
  rviz:=false
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

Fixed frame: `camera_init`

Suggested displays:
- `PointCloud2` → `/cloud_registered`
- `Path` → `/path`
- `TF`