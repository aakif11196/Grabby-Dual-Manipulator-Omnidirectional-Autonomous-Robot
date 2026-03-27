#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class ArmController(Node):
    def __init__(self):
        super().__init__("arm_controller_bridge")
        
        # Parameters
        self.declare_parameter("input_topic", "joint_commands")
        self.declare_parameter("arm_prefix", "vx300s_right")
        self.declare_parameter("output_joint_state_topic", "/arm_joint_states")
        
        self.input_topic = self.get_parameter("input_topic").value
        self.prefix = self.get_parameter("arm_prefix").value
        self.output_topic = self.get_parameter("output_joint_state_topic").value
        
        # Publishers for Gazebo Controllers
        self.arm_pub = self.create_publisher(JointTrajectory, f"/{self.prefix}_arm_controller/joint_trajectory", 10)
        self.gripper_pub = self.create_publisher(JointTrajectory, f"/{self.prefix}_gripper_controller/joint_trajectory", 10)
        
        # Publisher for RViz
        self.joint_state_pub = self.create_publisher(JointState, self.output_topic, 10)
        
        # Subscriber
        self.sub = self.create_subscription(JointState, self.input_topic, self.joint_callback, 10)
        
        self.get_logger().info(f"Arm Controller Bridge started for {self.prefix}")
    
    def joint_callback(self, msg):
        # Incoming from Serial Reader: waist, shoulder, elbow, wrist_angle, gripper
        if len(msg.position) < 5:
            return

        waist = msg.position[0]
        shoulder = msg.position[1]
        elbow = msg.position[2]
        wrist_angle = msg.position[3]
        gripper = msg.position[4]
        
        # --- 1. Publish to Gazebo Arm Controller (Match YAML list) ---
        arm_traj = JointTrajectory()
        arm_traj.joint_names = [
            f"{self.prefix}_waist",
            f"{self.prefix}_shoulder",
            f"{self.prefix}_elbow",
            f"{self.prefix}_forearm_roll", # Added to match your controllers.yaml
            f"{self.prefix}_wrist_angle",
        ]
        
        arm_point = JointTrajectoryPoint()
        # forearm_roll is set to 0.0 because it's not on your hardware
        arm_point.positions = [waist, shoulder, elbow, 0.0, wrist_angle]
        arm_point.time_from_start.nanosec = 100000000 # 100ms delay
        arm_traj.points.append(arm_point)
        self.arm_pub.publish(arm_traj)
        
        # --- 2. Publish to Gazebo Gripper Controller ---
        gripper_traj = JointTrajectory()
        gripper_traj.joint_names = [f"{self.prefix}_left_finger"]
        
        gripper_point = JointTrajectoryPoint()
        gripper_point.positions = [gripper]
        gripper_point.time_from_start.nanosec = 100000000
        gripper_traj.points.append(gripper_point)
        self.gripper_pub.publish(gripper_traj)
        
        # --- 3. Publish to RViz (All 7 Joints for Visualization) ---
        joint_state = JointState()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = arm_traj.joint_names + [
            f"{self.prefix}_left_finger",
            f"{self.prefix}_right_finger",
        ]
            
        joint_state.position = [
            waist, 
            shoulder, 
            elbow, 
            0.0,         # forearm_roll
            wrist_angle, 
            gripper,     # left finger
            -gripper     # right finger (mimic)
        ]
        self.joint_state_pub.publish(joint_state)

def main():
    rclpy.init()
    node = ArmController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()