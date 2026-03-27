# Grabby: Dual-Manipulator Omnidirectional Autonomous Robot

A state-of-the-art ROS 2 (Humble) based autonomous robot platform featuring dual 6-DOF manipulators and an omnidirectional base.

## 🚀 Overview
Grabby is designed for complex manipulation tasks in dynamic environments. It integrates advanced TF tree management, signal conditioning, and teleoperation capabilities.

### Key Features
- **Dual 6-DOF Manipulators**: Coordinated control of two interbotix-style arms.
- **Omnidirectional Base**: High-maneuverability movement using custom kinematics.
- **Gazebo Fortress Integration**: Full-physics simulation support.
- **ROS 2 Humble**: Leveraging the latest in robotic middleware for reliability and performance.
- **Autonomous Navigation**: Integrated with Nav2 for mapping and obstacle avoidance.

## 📁 Repository Structure
- `axebot_bringup`: Launch files and system configuration.
- `axebot_control`: Controller configurations and hardware interfaces.
- `axebot_description`: URDF models, meshes, and world files.
- `axebot_gazebo`: Simulation environment and spawning scripts.
- `omnidirectional_controllers`: Custom ROS 2 controllers for the base.

## 🛠️ Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/aakif11196/Grabby-Dual-Manipulator-Omnidirectional-Autonomous-Robot.git
   ```
2. Build the workspace:
   ```bash
   colcon build --symlink-install
   ```
3. Source the setup file:
   ```bash
   source install/setup.bash
   ```

## 🎮 Running the Simulation
To launch the robot in the warehouse environment:
```bash
ros2 launch axebot_gazebo axebot_launch.py
```

## 👤 Author
- **Shaikh Aakif** ([shaikhaakif278@gmail.com](mailto:shaikhaakif278@gmail.com))

---
*Built with ❤️ for the ROS 2 Community.*
