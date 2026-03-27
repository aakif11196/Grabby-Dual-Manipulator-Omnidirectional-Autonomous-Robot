#!/usr/bin/env python3
"""
Relay /cmd_vel -> /omnidirectional_controller/cmd_vel_unstamped
Nav2 publishes to /cmd_vel, but the ros2_control omnidirectional_controller
listens on /omnidirectional_controller/cmd_vel_unstamped.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelRelay(Node):
    def __init__(self):
        super().__init__('cmd_vel_relay', parameter_overrides=[
            rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)
        ])
        self.pub = self.create_publisher(
            Twist, '/omnidirectional_controller/cmd_vel_unstamped', 10)
        self.sub = self.create_subscription(
            Twist, '/cmd_vel', self.callback, 10)
        self.get_logger().info('Relaying /cmd_vel -> /omnidirectional_controller/cmd_vel_unstamped')

    def callback(self, msg):
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
