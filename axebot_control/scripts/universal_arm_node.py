#!/usr/bin/env python3
import serial, rclpy, time
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# Note: Humne JointState import hata diya hai kyunki hume Hardware se State nahi chahiye
# Hum Gazebo ki State use karenge.

class UniversalArmNode(Node):
    def __init__(self):
        super().__init__("universal_arm_node")
        
        # Parameters
        self.declare_parameter("port", "/dev/ttyACM0")
        self.declare_parameter("arm_prefix", "vx300s_right")
        # 'output_joint_state_topic' parameter HATA diya gaya hai
        
        self.port = self.get_parameter("port").value
        self.prefix = self.get_parameter("arm_prefix").value
        
        # Publishers (ONLY COMMANDS)
        # Gazebo Controllers ko command bhejne ke liye
        self.arm_pub = self.create_publisher(JointTrajectory, f"/{self.prefix}_arm_controller/joint_trajectory", 10)
        self.grip_pub = self.create_publisher(JointTrajectory, f"/{self.prefix}_gripper_controller/joint_trajectory", 10)
        
        self.arduino = None
        self.serial_buffer = ""
        self.execution_delay = 0.08 # Default faster speed (was 0.1s)
        self.debug_counter = 0
        self.connect_serial()
        self.create_timer(0.05, self.timer_callback) # 20Hz frequency

    def adjust_velocity(self, delay_sec):
        """
        Adjusts the velocity of the arm by changing the time_from_start delay.
        Lower delay = Higher velocity.
        """
        self.execution_delay = max(0.01, float(delay_sec)) # Prevent 0 or negative
        self.get_logger().info(f"Arm velocity delay set to: {self.execution_delay}s")

    def connect_serial(self):
        try:
            if self.arduino: self.arduino.close()
            self.arduino = serial.Serial(port=self.port, baudrate=115200, timeout=1.0)
            self.get_logger().info(f"Connected to {self.port} for {self.prefix}")
        except Exception as e:
            self.get_logger().warn(f"Waiting for {self.port}...")
            self.arduino = None

    def map_val(self, x, in_min, in_max, out_min, out_max):
        return (float(x) - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def timer_callback(self):
        if not self.arduino or not self.arduino.is_open:
            self.connect_serial(); return
        try:
            if self.arduino.in_waiting > 0:
                self.serial_buffer += self.arduino.read(self.arduino.in_waiting).decode("utf-8", errors="ignore")
            
            if "\n" in self.serial_buffer:
                lines = self.serial_buffer.split("\n")
                self.serial_buffer = lines[-1]
                
                for line in reversed(lines[:-1]):
                    vals = line.strip().split(",")
                    if len(vals) == 5:
                        try:
                            # 1. Parse Raw Values
                            v0 = int(float(vals[0]))
                            v1 = int(float(vals[1]))
                            v2 = int(float(vals[2]))
                            v3 = int(float(vals[3]))
                            # Simple float conversion handles "911." correctly as 911.0
                            v4 = int(float(vals[4])) 

                            # 2. Map Values
                            if "left" in self.prefix:
                                # Left Arm Specific Mapping (Shoulder Inverted)
                                a1 = self.map_val(v0, 0, 4095, -2.35, 2.35) #base
                                a2 = self.map_val(v1, 0, 4095, 2.35, -2.35) #shoulder (Inverted)
                                a3 = self.map_val(v2, 0, 4095, 2.35, -2.35) #elbow (Inverted)
                                a4 = self.map_val(v3, 0, 4095, 2.35, -2.35) #wrist
                                grip = self.map_val(v4, 0, 4095, 0.002, 0.057) #gripper - Meters
                            else:
                                # Right Arm Standard Mapping
                                a1 = self.map_val(vals[0], 0, 4095, -2.35, 2.35) #base
                                a2 = self.map_val(vals[1], 0, 4095, -2.35, 2.35) #shoulder
                                a3 = self.map_val(vals[2], 0, 4095, 2.35, -2.35) #elbow
                                a4 = self.map_val(vals[3], 0, 4095, 2.35, -2.35) #wrist
                                grip = self.map_val(vals[4], 0, 4095, 0.002, 0.057) #gripper


                            # Debug logging
                            self.debug_counter += 1
                            if self.debug_counter % 20 == 0:
                                self.get_logger().info(f"Publishing {self.prefix}: [{a1:.2f}, {a2:.2f}, {a3:.2f}, {a4:.2f}, {grip:.3f}]")

                            # 3. Publish Arm Trajectory
                            arm_m = JointTrajectory()
                            arm_m.header.stamp = self.get_clock().now().to_msg()
                            arm_m.joint_names = [
                                f"{self.prefix}_waist", 
                                f"{self.prefix}_shoulder", 
                                f"{self.prefix}_elbow", 
                                f"{self.prefix}_forearm_roll", 
                                f"{self.prefix}_wrist_angle"        
                            ]
                            p = JointTrajectoryPoint()
                            p.positions = [a1, a2, a3, 0.0, a4] 
                            p.time_from_start.nanosec = int(self.execution_delay * 1e9)
                            arm_m.points.append(p)
                            self.arm_pub.publish(arm_m)

                            # 4. Publish Gripper Trajectory
                            g_m = JointTrajectory()
                            g_m.header.stamp = self.get_clock().now().to_msg()
                            g_m.joint_names = [f"{self.prefix}_left_finger", f"{self.prefix}_right_finger"]
                            gp = JointTrajectoryPoint()
                            gp.positions = [grip, -grip]
                            gp.time_from_start.nanosec = int(self.execution_delay * 1e9)
                            g_m.points.append(gp)
                            self.grip_pub.publish(g_m)
                            break 
                        except ValueError as e:
                            # self.get_logger().warn(f"Parsing error: {e}")
                            continue
        except Exception as e: 
            pass

def main():
    rclpy.init()
    node = UniversalArmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()

if __name__ == '__main__': main()