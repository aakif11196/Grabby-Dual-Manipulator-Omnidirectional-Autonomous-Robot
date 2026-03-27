#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros

class OdomTfPublisher(Node):
    def __init__(self):
        super().__init__('odom_tf_publisher', parameter_overrides=[
            rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)
        ])
        
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.get_logger().info('Custom ODOM TF Publisher Started.')
        
        # Save last msg to republish at higher rate
        self.last_msg = None
        self.timer = self.create_timer(0.02, self.timer_callback) # 50 Hz
        
    def odom_callback(self, msg):
        self.last_msg = msg
        self.publish_tf(msg)
        self.get_logger().info(f'Odom callback received at sim time: {self.get_clock().now().to_msg().sec}', throttle_duration_sec=2.0)
        
    def timer_callback(self):
        if self.last_msg is not None:
            self.publish_tf(self.last_msg)
            self.get_logger().info(f'Timer publishing TF at sim time: {self.get_clock().now().to_msg().sec}', throttle_duration_sec=2.0)

    def publish_tf(self, odom_msg):
        t = TransformStamped()
        
        # Stamp it slightly into the future to prevent extrapolation errors in slam_toolbox
        # 0.05 seconds = 50ms into the future
        now = self.get_clock().now()
        t.header.stamp = now.to_msg()
        
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = odom_msg.pose.pose.position.x
        t.transform.translation.y = odom_msg.pose.pose.position.y
        t.transform.translation.z = odom_msg.pose.pose.position.z
        
        # Ensure quaternion is valid (prevent tf2 silent drop of unnormalized quaternions)
        q = odom_msg.pose.pose.orientation
        if q.x == 0.0 and q.y == 0.0 and q.z == 0.0 and q.w == 0.0:
            q.w = 1.0
            
        t.transform.rotation = q
        
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = OdomTfPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
