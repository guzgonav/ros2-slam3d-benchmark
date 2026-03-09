# Workspace Setup

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Livox SDK2 (required for FAST-LIO2)

## 1. Install Livox SDK2

Livox SDK2 needs a patch for GCC 14 (Ubuntu 24.04) due to missing `<cstdint>` includes:

```bash
cd /tmp
git clone https://github.com/Livox-SDK/Livox-SDK2.git
cd Livox-SDK2

# GCC 14 patch
grep -rl "uint8_t\|uint16_t\|uint32_t\|uint64_t" sdk_core/ --include="*.h" --include="*.hpp" | \
  xargs -I{} sed -i '1{/^#include <cstdint>/!i #include <cstdint>\n}' {}

mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
sudo ldconfig
```

## 2. Clone the workspace

```bash
git clone --recurse-submodules <this-repo>
cd slam_algorithms_ws
```

If you already cloned without `--recurse-submodules`:
```bash
git submodule update --init --recursive
```

## 3. Install ROS 2 dependencies

```bash
source /opt/ros/jazzy/setup.bash
sudo apt install \
  ros-jazzy-pcl-ros \
  ros-jazzy-pcl-conversions \
  ros-jazzy-tf2-ros \
  ros-jazzy-tf2-eigen \
  libpcl-dev \
  libeigen3-dev \
  libsuitesparse-dev
```

## 4. Install Python dependencies (KISS-SLAM)

KISS-SLAM requires a Python library with C++ extensions:

```bash
pip install kiss-slam --break-system-packages
```

> This is safe — `kiss-slam` is not in the Ubuntu package repos, so it won't conflict with any apt-managed packages.

## 5. Prepare KISS-SLAM for colcon

The `kiss-slam-ros2` submodule has a CMake target at its repo root (`kiss_slam_pybind`) that prevents colcon from finding the ROS2 package in the subdirectory. Two one-time steps are needed:

```bash
# Prevent colcon from treating the repo root as a cmake package
touch src/kiss-slam-ros2/COLCON_IGNORE

# Expose the ROS2 package directly to colcon
ln -s kiss-slam-ros2/ros2/src/kiss_slam_ros src/kiss_slam_ros
```

## 6. Build

`livox_ros_driver2` must be built first since `FAST_LIO` depends on it.

```bash
# Step 1: build livox driver
colcon build --packages-select livox_ros_driver2 \
  --cmake-args -DCMAKE_BUILD_TYPE=Release

# Step 2: source it, then build everything else
source install/setup.bash
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# Step 3: source the full workspace
source install/setup.bash
```

> **Note:** `livox_ros_driver2` auto-detects the ROS version via `$ENV{ROS_VERSION}` — no extra flags needed when ROS 2 Jazzy is sourced.

## Submodule details

| Submodule | Source | Branch |
|---|---|---|
| `lidarslam_ros2` | rsasaki0109/lidarslam_ros2 | main |
| `FAST_LIO` | guzgonav/FAST_LIO (fork of Ericsii) | ROS2 |
| `livox_ros_driver2` | Ericsii/livox_ros_driver2 | feature/use-standard-unit |
| `kiss-slam-ros2` | abwerby/kiss-slam-ros2 | main |