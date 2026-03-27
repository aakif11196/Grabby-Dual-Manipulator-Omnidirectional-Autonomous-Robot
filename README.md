# 🤖 Grabby — Omnidirectional Mobile Manipulation Robot

**Grabby** is a fully integrated ROS 2 research robot combining a 3-wheel omnidirectional mobile base with dual VX300s 6-DOF robotic arms simulated in Gazebo. The mobile base is teleoperated via keyboard (`cmd_vel`), while the simulated arms are driven in real time by two physical robotic exoskeletons worn by the operator — making it a unique human-in-the-loop manipulation research platform. It also supports fully autonomous navigation via Nav2 and SLAM-based mapping.

**⚠️ Note:** All ROS 2 packages in this repository use the axebot prefix (e.g., axebot_gazebo), which is the internal software name for the Grabby robot project.

---

## 📑 Table of Contents

- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Package Overview](#package-overview)
- [Hardware Components](#hardware-components)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Robot](#running-the-robot)
  - [Simulation (Gazebo)](#1-simulation-gazebo)
  - [Visualize in RViz only](#2-visualize-in-rviz-only)
  - [Exoskeleton Hardware Bringup](#3-exoskeleton-hardware-bringup)
  - [Navigation (Nav2 + SLAM)](#4-navigation-nav2--slam)
  - [Teleoperation (Base + Arms)](#5-teleoperation)
- [Configuration](#configuration)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Key Features

- **Omnidirectional mobility** — 3-wheel omni drive enables movement in any direction without turning
- **Dual robotic arms (simulated)** — left and right Interbotix VX300s arms (6-DOF each) running in Gazebo
- **Exoskeleton arm control** — each simulated arm is driven by a physical 3D-printed robotic exoskeleton worn by the operator, with 10K potentiometers + 12-bit ADC on ESP32 providing real-time joint feedback
- **Full ROS 2 integration** — ros2_control, Nav2, SLAM Toolbox, EKF odometry fusion
- **Mock LiDAR sensor** — simulated YDLiDAR with 12 m range used inside Gazebo for navigation and SLAM
- **Gazebo simulation** — complete digital twin for development and testing
- **Autonomous navigation** — path planning and obstacle avoidance via Nav2
- **Base teleoperation** — keyboard publishes `cmd_vel` to drive the mobile base manually
- **Exoskeleton firmware pipeline** — ESP32 reads potentiometer angles, applies a median filter to remove noise, and a ROS 2 node bridges the filtered joint values directly into the simulation

---

## 🧠 System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      User / Operator                         │
│   Keyboard (cmd_vel)  │  Nav2 Goal (RViz2)  │  Exoskeletons  │
└──────────┬────────────┴──────────┬──────────┴───────┬────────┘
           │                       │                  │
           │               ┌───────▼──────┐    ┌──────▼──────────────┐
           │               │  ROS 2       │    │  Exoskeleton Bridge  │
           │               │  Nav2 Stack  │    │(universal_arm_node.py)│
           │               │  SLAM Toolbox│    │                      │
           │               │  EKF Fusion  │    │  ESP32 (×2)          │
           │               └───────┬──────┘    │  ├─ 10K Pots (ADC)   │
           │                       │           │  ├─ Median Filter    │
           │               ┌───────▼──────────-┴──▼──────────────┐    │
           │               │         ROS 2 (Humble)               │   │
           └───────────────►  ros2_control / Controllers          │   │
                           │  OmniDir Controller │ Arm Controllers │  │
                           └─────────────────────┴───────────────-┘   │
                                         │                            │
                           ┌─────────────▼─────────────────────────┐  │
                           │         GAZEBO SIMULATION             │  │
                           │  ┌──────────────┐  ┌───────────────┐  │  │
                           │  │  3-Wheel Omni│  │ Dual VX300s   │◄─┘  │
                           │  │  Drive Base  │  │ Arms (L + R)  │     │
                           │  └──────────────┘  └───────────────┘     │
                           │  ┌─────────────────────────────────┐     │
                           │  │  Mock LiDAR (12 m range)        │     │
                           │  └─────────────────────────────────┘     │
                           └────────────────────────────────────────-─┘
```

The robot's software is organized into focused ROS 2 packages, each responsible for a specific layer of the system (description, control, navigation, and simulation). All packages are built with `colcon` and follow the `ament_cmake` / `ament_python` build systems.

---

## 📦 Package Overview

| Package | Type | Purpose |
|---|---|---|
| `axebot_description` | ament_cmake | URDF/Xacro robot model, meshes, RViz configs, world files |
| `axebot_control` | ament_cmake | Hardware controllers, arm scripts, serial firmware bridge |
| `axebot_bringup` | ament_cmake | Top-level launch files for navigation, simulation, and digital twin |
| `axebot_gazebo` | ament_cmake | Gazebo simulation launch and world definitions |
| `omnidirectional_controllers` | ament_cmake | Custom ros2_control plugin for mecanum/omni wheel kinematics and odometry |
| `custom_teleop_twist_keyboard` | ament_python | Modified keyboard teleop node for manual control |

### Package Details

**`axebot_description`**
Defines the complete physical structure of the robot using URDF/Xacro files. Contains separate xacro modules for the base, wheels, arms (left/right VX300s), sensors, Gazebo plugins, and ros2_control hardware interfaces. Also includes RViz2 configuration presets and Gazebo world files.

**`axebot_control`**
Contains all runtime control logic. Python scripts handle serial communication with the ESP32 exoskeleton microcontrollers (`universal_serial_reader.py`), arm joint control (`universal_arm_node.py`), and odometry/TF publishing. C++ nodes include the `exo_bridge_node` which receives filtered potentiometer joint angles from the exoskeleton firmware and maps them to the simulated VX300s arm joints, and a `go_to_goal` controller for position-based navigation.

**`axebot_bringup`**
The entry point for launching the full robot system. Provides three key launch files: `sim_viz.launch.py` for simulation + visualization, `digital_twin.launch.py` for running a synchronized digital copy alongside real hardware, and `navigation_launch.py` for the full Nav2 + SLAM stack.

**`omnidirectional_controllers`**
A custom ros2_control plugin implementing mecanum wheel forward/inverse kinematics and wheel odometry. Registered as a pluginlib plugin (`controller_interface`) and tested with GTest-based unit tests for both kinematics and odometry modules.

---

## 🔧 Hardware Components

| Component | Details |
|---|---|
| **Drive System** | 3× omnidirectional wheels |
| **Robotic Arms** | 2× Interbotix VX300s (6-DOF, left + right) — simulated in Gazebo |
| **Arm Exoskeletons** | 2× custom 3D-printed robotic exoskeletons (one per arm), worn by the operator |
| **Exoskeleton Sensing** | 10 KΩ potentiometers per joint for angular feedback |
| **Exoskeleton MCU** | ESP32 with 12-bit ADC — reads pot values, applies median filter, sends over serial |
| **LiDAR** | Mock hardware LiDAR (simulated, 12 m range) used inside Gazebo for Nav2 and SLAM |
| **Compute** | PC running ROS 2 Humble + Gazebo |

---

## ✅ Prerequisites

Before setting up axebot, make sure you have the following installed:

**Operating System:** Ubuntu 22.04 (Jammy)

**ROS 2 Humble** — Full desktop install recommended:
```bash
# Follow the official guide: https://docs.ros.org/en/humble/Installation.html
sudo apt install ros-humble-desktop
```

**Required ROS 2 packages:**
```bash
sudo apt install \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-localization \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control \
  ros-humble-xacro \
  ros-humble-joint-state-publisher-gui \
  ros-humble-robot-state-publisher
```

**Python dependencies:**
```bash
pip3 install pyserial
```

---

## 🚀 Installation

### 1. Create your workspace and clone the repository

```bash
mkdir -p ~/axebot_ws
cd ~/axebot_ws
git clone <repository-url> axebot
```

### 2. Install dependencies

```bash
cd ~/axebot_ws
rosdep install --from-paths axebot --ignore-src -r -y
```

### 3. Build the workspace

```bash
cd ~/axebot_ws
colcon build --symlink-install
```

> `--symlink-install` is recommended during development — it creates symlinks instead of copying files, so changes to Python scripts and launch files take effect immediately without rebuilding.

### 4. Source the workspace

```bash
source ~/axebot_ws/axebot/install/setup.bash
```

Add this to your `~/.bashrc` to source it automatically on every terminal:
```bash
echo "source ~/axebot_ws/axebot/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 🎮 Running the Robot

### 1. Simulation (Gazebo)

Launch the full robot in a Gazebo simulation environment with all controllers active:

```bash
ros2 launch axebot_gazebo axebot_launch.py
```

To spawn the robot only (without the full stack):
```bash
ros2 launch axebot_gazebo spawn_axebot.launch.py
```

### 2. Visualize in RViz Only

To view the robot model in RViz2 without simulation (useful for URDF development and checking transforms):

```bash
ros2 launch axebot_description view_robot.launch.py
```

To visualize in simulation mode with the full Gazebo + RViz2 combination:
```bash
ros2 launch axebot_bringup sim_viz.launch.py
```

### 3. Exoskeleton Hardware Bringup

The only physical hardware in the system is the pair of robotic exoskeletons. To start the exoskeleton firmware bridge (which reads pot values from the ESP32 and drives the simulated arms):

```bash
ros2 launch axebot_control firmware.launch.py
```

For the digital twin (Gazebo simulation synchronized alongside):
```bash
ros2 launch axebot_bringup digital_twin.launch.py
```

### 4. Navigation (Nav2 + SLAM)

To run full autonomous navigation with real-time SLAM mapping:

```bash
ros2 launch axebot_bringup navigation_launch.py
```

This launches:
- **Nav2** — for global/local path planning and obstacle avoidance
- **SLAM Toolbox** (async mode) — for real-time map building
- **EKF (robot_localization)** — for fusing wheel odometry and IMU data into a reliable pose estimate

Once running, use RViz2 to:
1. Set a **2D Pose Estimate** to initialize the robot's position
2. Use **Nav2 Goal** to send the robot to any location on the map

### 5. Teleoperation

Axebot uses **two separate control methods** — one for the mobile base and one for the arms.

#### 5a. Base — Keyboard Teleoperation

The mobile base is driven by publishing `cmd_vel` via keyboard:

```bash
ros2 run teleop_twist_keyboard_custom teleop_twist_keyboard
```

Default key bindings:

| Key | Action |
|---|---|
| `i` | Move forward |
| `,` | Move backward |
| `j` | Strafe left |
| `l` | Strafe right |
| `u / o` | Diagonal movement |
| `k` | Stop |
| `q / z` | Increase / decrease speed |

#### 5b. 🕹️ Arms — **Physical Exoskeleton Control**

The simulated arms are controlled in real time by two **physical robotic exoskeletons** worn by the operator. Each exoskeleton maps directly to one simulated VX300s arm (left and right).

**How the exoskeleton pipeline works:**

```
Operator moves exoskeleton
        │
        ▼
10K potentiometers measure joint angles
        │
        ▼
ESP32 reads values via 12-bit ADC
        │
        ▼
Firmware applies median filter (removes potentiometer noise)
        │
        ▼
Filtered joint values sent over serial (USB)
        │
        ▼
ROS 2 node (exo_bridge_node) reads serial data
        │
        ▼
Joint positions published → Simulated VX300s arm moves
```

To launch the exoskeleton bridge node:

```bash
ros2 launch axebot_control firmware.launch.py
```

> **Note:** Ensure the ESP32 exoskeleton controllers are connected via USB before launching. Check device ports with:
> ```bash
> ls /dev/ttyUSB* /dev/ttyACM*
> ```
> Grant serial permissions if needed:
> ```bash
> sudo usermod -aG dialout $USER
> # Log out and back in for this to take effect
> ```

---

## ⚙️ Configuration

All configuration files are located in the `config/` directories of each package:

| File | Location | Purpose |
|---|---|---|
| `ekf.yaml` | `axebot_bringup/config/` | Extended Kalman Filter parameters for odometry fusion |
| `nav2_params.yaml` | `axebot_bringup/config/` | Nav2 planner, controller, and costmap settings |
| `mapper_params_online_async.yaml` | `axebot_bringup/config/` | SLAM Toolbox async mapping parameters |
| `omnidirectional_controller.yaml` | `axebot_control/config/` | Mecanum wheel controller gains and wheel geometry |
| `ros2_controllers.yaml` | `axebot_control/config/` | ros2_control hardware interface config |
| `vx300s_controllers.yaml` | `axebot_control/config/` | VX300s arm joint controllers |

### Key Parameters to Tune

**Omnidirectional controller** (`omnidirectional_controller.yaml`) — set your wheel radius and base geometry to match your physical robot.

**EKF** (`ekf.yaml`) — configure which sensor sources (odom, IMU) are fused and their noise covariances.

**Nav2** (`nav2_params.yaml`) — tune the local/global costmap resolution, inflation radius, and controller velocity limits to match your robot's speed and environment.

---

## 📁 Repository Structure

```
axebot/
├── axebot_bringup/          # Top-level launch files (navigation, sim, digital twin)
├── axebot_control/          # Hardware controllers, arm scripts, serial bridge
├── axebot_description/      # URDF/Xacro model, meshes, RViz configs, worlds
├── axebot_gazebo/           # Gazebo simulation launch and world files
├── omnidirectional_controllers/  # Custom mecanum wheel ros2_control plugin
├── custom_teleop_twist_keyboard/ # Modified keyboard teleoperation node
├── build/                   # Colcon build artifacts (do not edit)
├── install/                 # Installed package files (do not edit)
├── log/                     # Build and runtime logs
└── README.md
```

---

## 📊 Project Status

| Feature | Status |
|---|---|
| Omnidirectional drive (simulation) | ✅ Working |
| Dual VX300s arm control (simulation) | ✅ Working |
| Exoskeleton → simulation arm control | ✅ Working |
| Exoskeleton firmware (ESP32 + median filter) | ✅ Working |
| SLAM mapping | ✅ Working |
| Nav2 autonomous navigation | ✅ Working |
| EKF odometry fusion | ✅ Working |
| Gazebo digital twin | ✅ Working |
| Keyboard base teleoperation | ✅ Working |

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or want to add a feature:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please make sure your code follows the ROS 2 coding conventions and passes `ament_lint` checks before submitting.

---

## 📜 License

This project is open-source. See the `LICENSE` file for details.

---

*Built with ROS 2 Humble · Ubuntu 22.04 · Gazebo · Nav2 · SLAM Toolbox*
