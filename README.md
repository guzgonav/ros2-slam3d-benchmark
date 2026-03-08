# SLAM Algorithms Workspace

ROS 2 (Jazzy) workspace for benchmarking 3D LiDAR SLAM algorithms on the Oxford Spires dataset.

## Algorithms

| Algorithm | Description | Doc |
|---|---|---|
| lidarslam | Scan-matching + graph-based SLAM (NDT) | [docs/lidarslam.md](docs/lidarslam.md) |
| FAST-LIO2 | Tightly-coupled LiDAR-IMU odometry (iKD-Tree) | [docs/fast_lio.md](docs/fast_lio.md) |

## Workspace Structure

```
src/
  slam_benchmarks/      # Launch files and configs for all algorithms
  lidarslam_ros2/       # Submodule: rsasaki0109/lidarslam_ros2
  FAST_LIO/             # Submodule: guzgonav/FAST_LIO (ROS2 branch)
  livox_ros_driver2/    # Submodule: Ericsii/livox_ros_driver2
docs/
  setup.md              # Prerequisites and workspace build instructions
  lidarslam.md          # lidarslam setup and usage
  fast_lio.md           # FAST-LIO2 setup and usage
```

## Quick Start

See [docs/setup.md](docs/setup.md) for full prerequisites and build instructions.

```bash
git clone --recurse-submodules <this-repo>
cd slam_algorithms_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select livox_ros_driver2 --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```