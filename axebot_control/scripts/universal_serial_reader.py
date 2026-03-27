#!/usr/bin/env python3
import serial
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class UniversalSerialReader(Node):
    def __init__(self):
        super().__init__("universal_serial_reader")
        
        # Parameters
        self.declare_parameter("port", "/dev/ttyACM0")
        self.declare_parameter("baudrate", 115200)
        self.declare_parameter("topic_name", "joint_commands")
        self.declare_parameter("min_angle", -2.356)
        self.declare_parameter("max_angle", 2.356)
        # Deadband: ignore ADC changes smaller than this threshold (prevents flickering)
        # 15 counts out of 4095 ≈ 0.02 rad — filters noise but allows intentional moves
        self.declare_parameter("deadband_threshold", 15)
        
        self.port = self.get_parameter("port").value
        self.baudrate = self.get_parameter("baudrate").value
        self.topic_name = self.get_parameter("topic_name").value
        self.min_angle = self.get_parameter("min_angle").value
        self.max_angle = self.get_parameter("max_angle").value
        self.deadband = self.get_parameter("deadband_threshold").value
        
        # Publisher
        self.pub = self.create_publisher(JointState, self.topic_name, 10)
        
        self.arduino = None
        self.last_connection_attempt = 0
        self.connect_serial()
        
        # Timer for reading (20Hz)
        self.timer = self.create_timer(0.05, self.timer_callback)
        # Buffer for incomplete lines
        self.serial_buffer = ""
        # Store last published raw values for deadband comparison
        self.last_raw_values = None
        
    def connect_serial(self):
        try:
            if self.arduino:
                self.arduino.close()
            self.arduino = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=1.0)
            self.get_logger().info(f"Connected to {self.port}")
        except serial.SerialException as e:
            # Only log every 5 seconds to avoid spamming
            current_time = time.time()
            if current_time - self.last_connection_attempt > 5.0:
                self.get_logger().warn(f"Failed to connect to {self.port}: {e}. Retrying...")
                self.last_connection_attempt = current_time
            self.arduino = None

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def timer_callback(self):
        if not self.arduino or not self.arduino.is_open:
            self.connect_serial()
            return

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
                raw_values = [raw_1, raw_2, raw_3, raw_4, raw_5]
                
                # --- Deadband filter: skip if no channel changed significantly ---
                if self.last_raw_values is not None:
                    max_change = max(abs(a - b) for a, b in zip(raw_values, self.last_raw_values))
                    if max_change < self.deadband:
                        return  # Noise only — skip this reading
                
                # Update stored values (only when we actually publish)
                self.last_raw_values = raw_values
                
                # Map to angles (unchanged logic)
                angle_1 = float(self.map_value(raw_1, 0, 4095, self.min_angle, self.max_angle))
                angle_2 = float(self.map_value(raw_2, 0, 4095, self.min_angle, self.max_angle))
                angle_3 = float(self.map_value(raw_3, 0, 4095, self.max_angle, self.min_angle))
                angle_4 = float(self.map_value(raw_4, 0, 4095, self.min_angle, self.max_angle))
                # Gripper is prismatic: 0.021 (closed) to 0.057 (open)
                angle_5 = float(self.map_value(raw_5, 0, 4095, 0.021, 0.057))
                
                # Publish as JointState
                msg = JointState()
                msg.header.stamp = self.get_clock().now().to_msg()
                # Use generic names here, the bridge will map them to specific joints
                msg.name = ["waist", "shoulder", "elbow", "wrist_angle", "gripper"]
                msg.position = [angle_1, angle_2, angle_3, angle_4, angle_5]
                msg.velocity = []
                msg.effort = []
                
                self.pub.publish(msg)

        except Exception as e:
            self.get_logger().warn(f"Error reading serial: {e}")
            self.arduino = None # Force reconnection on validity error

def main():
    rclpy.init()
    node = UniversalSerialReader()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
