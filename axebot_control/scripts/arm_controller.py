#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class ArmController(Node):
    def __init__(self):
        super().__init__("arm_controller_bridge")
        
        # Publishers for Gazebo Controllers
        self.arm_pub = self.create_publisher(JointTrajectory, "/vx300s_right_arm_controller/joint_trajectory", 10)
        self.gripper_pub = self.create_publisher(JointTrajectory, "/vx300s_right_gripper_controller/joint_trajectory", 10)
        
        # Publisher for RViz
        self.joint_state_pub = self.create_publisher(JointState, "/arm_joint_states", 10)
        
        # Subscriber
        self.sub = self.create_subscription(JointState, "joint_commands", self.joint_callback, 10)
        
        self.get_logger().info("Grabby Arm Controller Bridge started")
    
    def joint_callback(self, msg):
        # Map incoming 5 joints to full 6 DOF arm + gripper
        # Incoming: waist, shoulder, elbow, wrist_angle, gripper
        
        if len(msg.position) < 5:
            return

        waist = msg.position[0]
        shoulder = msg.position[1]
        elbow = msg.position[2]
        wrist_angle = msg.position[3]
        gripper = msg.position[4]
        
        # Publish to Gazebo (arm_controller)
        arm_traj = JointTrajectory()
        arm_traj.joint_names = [
            "vx300s_right_waist",
            "vx300s_right_shoulder",
            "vx300s_right_elbow",
            "vx300s_right_wrist_angle",
        ]
        
        arm_point = JointTrajectoryPoint()
        arm_point.positions = [waist, shoulder, elbow, wrist_angle]
        arm_point.time_from_start.sec = 0
        arm_point.time_from_start.nanosec = 100000000 # 100ms
        arm_traj.points.append(arm_point)
        
        self.arm_pub.publish(arm_traj)
        
        # Publish to Gazebo (gripper_controller)
        gripper_traj = JointTrajectory()
        gripper_traj.joint_names = ["vx300s_right_left_finger"]
        
        gripper_point = JointTrajectoryPoint()
        gripper_point.positions = [gripper]
        gripper_point.time_from_start.sec = 0
        gripper_point.time_from_start.nanosec = 100000000 #100ms
        gripper_traj.points.append(gripper_point)
        
        self.gripper_pub.publish(gripper_traj)
        
        # Publish to RViz (joint_states)
        joint_state = JointState()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = [
            "vx300s_right_waist",
            "vx300s_right_shoulder",
            "vx300s_right_elbow",
            "vx300s_right_wrist_angle",
            "vx300s_right_left_finger",
            "vx300s_right_right_finger",
        ]
            
        joint_state.position = [
            waist, 
            shoulder, 
            elbow, 
            wrist_angle, 
            gripper, # left finger
            -gripper  # right finger
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
