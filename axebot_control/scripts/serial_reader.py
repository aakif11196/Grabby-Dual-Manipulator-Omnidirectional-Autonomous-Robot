#!/usr/bin/env python3
import serial
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class PotSerialReader(Node):
    def __init__(self):
        super().__init__("pot_serial_reader")
        
        # Parameters
        self.declare_parameter("port", "/dev/ttyACM0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("min_angle", -2.356)
        self.declare_parameter("max_angle", 2.356)
        
        port = self.get_parameter("port").value
        baudrate = self.get_parameter("baudrate").value
        self.min_angle = self.get_parameter("min_angle").value
        self.max_angle = self.get_parameter("max_angle").value
        
        # Publisher
        self.pub = self.create_publisher(JointState, "joint_commands", 10)
        
        # Serial connection
        try:
            self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1.0)
            self.get_logger().info(f"Connected to {port}")
        except serial.SerialException as e:
            self.get_logger().warn(f"Failed to connect to {port}: {e}. Running in mock mode.")
            self.arduino = None
        
        # Timer for reading (100Hz)
        self.timer = self.create_timer(0.01, self.timer_callback)
        # Buffer for incomplete lines
        self.serial_buffer = ""
        
    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def timer_callback(self):
        if rclpy.ok():
            if self.arduino and self.arduino.is_open:
                try:
                    if self.arduino.in_waiting > 0:
                        # Read only available bytes
                        data_bytes = self.arduino.read(self.arduino.in_waiting)
                        try:
                            data_str = data_bytes.decode("utf-8", errors="ignore")
                            self.serial_buffer += data_str
                        except Exception:
                            pass
                    
                    if "\n" in self.serial_buffer:
                        lines = self.serial_buffer.split("\n")
                        # The last element is either empty (if ended with \n) or incomplete
                        self.serial_buffer = lines[-1]
                        
                        # Process all complete lines (reversed to find latest valid)
                        valid_line = None
                        for line in reversed(lines[:-1]):
                            line = line.strip()
                            if line and line.count(",") == 4:
                                valid_line = line
                                break
                        
                        if not valid_line:
                            return
                        
                        # self.get_logger().info(f"Valid: {valid_line}")
                        
                        # Split CSV values
                        values = valid_line.split(",")
                        
                        # Parse as floats first
                        try:
                            raw_1 = int(float(values[0]))
                            raw_2 = int(float(values[1]))
                            raw_3 = int(float(values[2]))
                            raw_4 = int(float(values[3]))
                            raw_5 = int(float(values[4]))
                        except ValueError:
                            return
                        
                        # Map to angles
                        angle_1 = self.map_value(raw_1, 0, 4095, self.min_angle, self.max_angle)
                        angle_2 = self.map_value(raw_2, 0, 4095, self.min_angle, self.max_angle)
                        angle_3 = self.map_value(raw_3, 0, 4095, self.max_angle, self.min_angle)
                        angle_4 = self.map_value(raw_4, 0, 4095, self.min_angle, self.max_angle)
                        # Gripper is prismatic: 0.021 (closed) to 0.057 (open)
                        angle_5 = self.map_value(raw_5, 0, 4095, 0.021, 0.057)
                        
                        # Publish as JointState
                        msg = JointState()
                        # Mapping 5 inputs to 5 main joints of Axebot
                        msg.name = [
                            "vx300s_right_waist", 
                            "vx300s_right_shoulder", 
                            "vx300s_right_elbow", 
                            "vx300s_right_wrist_angle",
                            "vx300s_right_left_finger",
                        ]
                        msg.position = [angle_1, angle_2, angle_3, angle_4, angle_5]
                        
                        self.pub.publish(msg)

                except Exception as e:
                    self.get_logger().warn(f"Error reading serial: {e}")
                    pass
                    
                    # Map to angles
                    angle_1 = self.map_value(raw_1, 0, 4095, self.min_angle, self.max_angle)
                    angle_2 = self.map_value(raw_2, 0, 4095, self.min_angle, self.max_angle)
                    angle_3 = self.map_value(raw_3, 0, 4095, self.max_angle, self.min_angle)
                    angle_4 = self.map_value(raw_4, 0, 4095, self.min_angle, self.max_angle)
                    # Gripper is prismatic: 0.021 (closed) to 0.057 (open)
                    angle_5 = self.map_value(raw_5, 0, 4095, 0.021, 0.057)
                    
                    # Publish as JointState
                    msg = JointState()
                    # Mapping 5 inputs to 5 main joints of Axebot
                    msg.name = [
                        "vx300s_right_waist", 
                        "vx300s_right_shoulder", 
                        "vx300s_right_elbow", 
                        "vx300s_right_wrist_angle",
                        "vx300s_right_left_finger",
                    ]
                    msg.position = [angle_1, angle_2, angle_3, angle_4, angle_5]
                    
                    self.pub.publish(msg)
                    
                except Exception as e:
                    self.get_logger().warn(f"Error reading serial: {e}")
                    pass
            else:
                # Mock mode or disconnected
                pass

def main():
    rclpy.init()
    node = PotSerialReader()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
