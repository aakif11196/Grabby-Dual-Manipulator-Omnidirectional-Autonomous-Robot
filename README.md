# 🤖 Grabby: Dual-Manipulator Omnidirectional Autonomous Robot

![Grabby Robot Showcase](doc/images/grabby_hero.jpg) 
*(Note: Replace `doc/images/grabby_hero.jpg` with the actual path to your robot image in your repository)*

A state-of-the-art ROS 2 (Humble) autonomous mobile robot platform featuring dual 6-DOF manipulators (ViperX 300s style) and an omnidirectional base. Grabby is built to handle complex manipulation tasks, advanced TF tree synchronization, and bidirectional digital-twin teleoperation in dynamic environments.

---

## 🚀 Core Features

* **Dual 6-DOF Manipulators:** Coordinated trajectory control of two high-precision arms for advanced pick-and-place tasks.
* **Omnidirectional Base:** Custom C++ kinematics plugin for high-maneuverability holonomic movement.
* **Gazebo Fortress Integration:** Full-physics simulation support within a custom warehouse environment.
* **Exoskeleton Digital Twin:** Built-in signal conditioning (Median/EMA filters) bridging noisy physical human exoskeleton movements directly to the simulated joint states.
* **Autonomous Navigation (Nav2):** Dynamic obstacle avoidance, rolling costmaps, and EKF sensor fusion mapping.

---

## 💻 System Requirements

To ensure smooth performance when running the physics simulator, Nav2, and the dual-arm controllers simultaneously, the following system specifications are required:

* **OS:** Ubuntu 22.04 LTS (Jammy Jellyfish)
* **Middleware:** ROS 2 Humble Hawksbill
* **Simulation:** Gazebo Fortress (or Gazebo 11 Classic depending on your specific ignition setup)
* **Memory (RAM):** 16GB Minimum (32GB Highly Recommended for rendering Gazebo + Nav2 Costmaps)
* **Processor:** Modern Multi-core CPU (Intel i7/i9 or AMD Ryzen 7/9)
* **Graphics:** Dedicated GPU (NVIDIA RTX 3060 or better) recommended for stable simulation framerates.

---

## 📁 Repository Structure

* **`axebot_bringup`**: Top-level launch files, EKF/SLAM parameter tuning, and RViz configurations.
* **`axebot_control`**: Custom C++ control logic, embedded hardware interfaces, exoskeleton bridge nodes, and Python arm trajectory scripts.
* **`axebot_description`**: URDF/Xacro kinematic models, 3D meshes (chassis, LiDAR, manipulators), and Gazebo SDF worlds.
* **`axebot_gazebo`**: Gazebo simulation environments and spawning scripts.
* **`omnidirectional_controllers`**: Custom ROS 2 plugin managing forward/inverse kinematics for the omni-wheels.

---

## 🗺️ TF Tree Architecture

Maintaining absolute spatial awareness across an omnidirectional base, a vertical lift, and 12 total manipulator joints requires a highly synchronized TF tree.

![Grabby TF Tree](doc/images/tf_tree.png)
*(Note: Upload your TF tree PDF/Image here to show off your coordinate frame architecture)*

---

## ⚙️ Launch Files Directory

Here is a breakdown of the primary launch files to execute different subsystems of Grabby:

### 1. `axebot_launch.py` (Simulation Base)
**Location:** `axebot_gazebo/launch/`
**Purpose:** Spawns the entire Grabby robot model inside the Gazebo physical environment (Warehouse map). It loads the physics engine, collision meshes, and simulated sensors (LiDAR, Camera, Odom).

### 2. `sim_viz.launch.py` (Visualization)
**Location:** `axebot_bringup/launch/`
**Purpose:** Ignites the `robot_state_publisher` and `joint_state_publisher`. It calculates the massive 13+ DOF TF tree in real-time and opens RViz2 so you can visualize the sensor data and robot joints.

### 3. `digital_twin.launch.py` (Teleoperation Bridge)
**Location:** `axebot_bringup/launch/`
**Purpose:** Spins up the custom C++ Exo-to-Joint bridge nodes. This launch file listens for incoming serial data from the physical human exoskeleton, filters the analog noise, and translates it into `JointTrajectory` messages for the simulated manipulators.

### 4. `navigation_launch.py` (Autonomy Brain)
**Location:** `axebot_bringup/launch/`
**Purpose:** The core autonomy stack. It launches the Extended Kalman Filter (EKF) to fuse Odometry and GPS data, starts the Nav2 costmap servers, and enables autonomous waypoint routing and dynamic obstacle avoidance.

---

## 🛠️ Installation & Setup

**1. Clone the repository into your ROS 2 workspace:**
```bash
mkdir -p ~/grabby_ws/src
cd ~/grabby_ws/src
git clone https://github.com/aakif11196/Grabby-Dual-Manipulator-Omnidirectional-Autonomous-Robot.git
```
