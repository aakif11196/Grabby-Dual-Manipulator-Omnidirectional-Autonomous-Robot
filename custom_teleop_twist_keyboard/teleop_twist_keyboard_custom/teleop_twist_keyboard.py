#!/usr/bin/python3
# EASY-INSTALL-ENTRY-SCRIPT: 'teleop-twist-keyboard==2.4.0','console_scripts','teleop_twist_keyboard'

import sys
import threading
import re
import time
import math

import geometry_msgs.msg
import rclpy

if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

msg = """
This node takes keypresses from the keyboard and publishes them
as Twist/TwistStamped messages. It works best with a US keyboard layout.
---------------------------
Moving around:
      u    i    o
  h   j    k    l   ;
      m    ,    .

For Holonomic mode (strafing), hold down the shift key:
---------------------------
      U    I    O
  H   J    K    L   :
      M    <    >


anything else : stop

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%

CTRL-C to quit


Moving around (short defs):
 
  i : Forward        (straight)
  k : Backward       (reverse)
  j : Turn Left      (rotate left)
  l : Turn Right     (rotate right)
  o : Forward-Right  (diagonal)
  u : Forward-Left   (diagonal)
  h : Strafe Left    (sideways left)
  ; : Strafe Right   (sideways right)
  t : rotate 180 degrees in place (uses current angular speed)
  spacebar : Emergency Stop (no motion)
"""

diag = 0.7071067811865476

# movement keys
moveBindings = {
    'i': (1, 0, 0, 0),
    'o': (diag, -diag, 0, 0),
    'j': (0, 0, 0, 1),
    'l': (0, 0, 0, -1),
    'u': (diag, diag, 0, 0),
    'k': (-1, 0, 0, 0),
    '.': (-1, 0, 0, 1),
    'm': (-1, 0, 0, -1),
    'O': (1, 1, 0, 0),
    'I': (1, 0, 0, 0),
    'J': (0, 1, 0, 0),
    'L': (0, -1, 0, 0),
    'U': (1, -1, 0, 0),
    'K': (-1, 0, 0, 0),
    '>': (-1, -1, 0, 0),
    'M': (-1, 1, 0, 0),
    't': (0, 0, 1, 0),
    'b': (0, 0, -1, 0),
    ' ': (0, 0, 0, 0),
    'h': (0, 1, 0, 0),
    ';': (0, -1, 0, 0),
}

# speed keys
speedBindings = {
    'q': (1.1, 1.1),
    'z': (.9, .9),
    'w': (1.1, 1),
    'x': (.9, 1),
    'e': (1, 1.1),
    'c': (1, .9),
}


def getKey(settings):
    if sys.platform == 'win32':
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def vels(speed, turn):
    return f'currently:\tspeed {speed}\tturn {turn}'


def rotate_180(pub, twist_msg, twist, angular_speed, stamped, node, rate_hz=20.0):
    """
    Rotate in-place 180 degrees (pi radians) using open-loop timing.
    angular_speed: positive scalar in rad/s (we rotate CCW). If 0, fallback to 1.0.
    """
    if angular_speed == 0:
        angular_speed = 1.0
    duration = math.pi / abs(angular_speed)  # seconds to rotate pi radians
    dt = 1.0 / rate_hz
    end_time = time.time() + duration

    while time.time() < end_time:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist.linear.x = twist.linear.y = twist.linear.z = 0.0
        twist.angular.x = twist.angular.y = 0.0
        twist.angular.z = angular_speed  # CCW rotation
        pub.publish(twist_msg)
        time.sleep(dt)

    # stop rotation
    if stamped:
        twist_msg.header.stamp = node.get_clock().now().to_msg()
    twist.angular.z = 0.0
    pub.publish(twist_msg)


def main():
    settings = saveTerminalSettings()

    rclpy.init()
    node = rclpy.create_node('teleop_twist_keyboard')

    # parameters
    stamped = node.declare_parameter('stamped', False).value
    frame_id = node.declare_parameter('frame_id', '').value
    if not stamped and frame_id:
        raise Exception("'frame_id' can only be set when 'stamped' is True")

    TwistMsg = geometry_msgs.msg.TwistStamped if stamped else geometry_msgs.msg.Twist

    pub = node.create_publisher(TwistMsg, 'cmd_vel', 10)

    spinner = threading.Thread(target=rclpy.spin, args=(node,))
    spinner.start()

    speed = 0.5
    turn = 1.0
    x = y = z = th = 0.0
    status = 0

    twist_msg = TwistMsg()
    if stamped:
        twist = twist_msg.twist
        twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist_msg.header.frame_id = frame_id
    else:
        twist = twist_msg

    try:
        print(msg)
        print(vels(speed, turn))
        while True:
            key = getKey(settings)
#!/usr/bin/python3
# EASY-INSTALL-ENTRY-SCRIPT: 'teleop-twist-keyboard==2.4.0','console_scripts','teleop_twist_keyboard'

import sys
import threading
import re
import time
import math

import geometry_msgs.msg
import rclpy

if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

msg = """
This node takes keypresses from the keyboard and publishes them
as Twist/TwistStamped messages. It works best with a US keyboard layout.
---------------------------
Moving around:
      u    i    o
  h   j    k    l   ;
      m    ,    .

For Holonomic mode (strafing), hold down the shift key:
---------------------------
      U    I    O
  H   J    K    L   :
      M    <    >


anything else : stop

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%

CTRL-C to quit


Moving around (short defs):
 
  i : Forward        (straight)
  k : Backward       (reverse)
  j : Turn Left      (rotate left)
  l : Turn Right     (rotate right)
  o : Forward-Right  (diagonal)
  u : Forward-Left   (diagonal)
  h : Strafe Left    (sideways left)
  ; : Strafe Right   (sideways right)
  t : rotate 180 degrees in place (uses current angular speed)
  spacebar : Emergency Stop (no motion)
"""

diag = 0.7071067811865476

# movement keys
moveBindings = {
    'i': (1, 0, 0, 0),
    'o': (diag, -diag, 0, 0),
    'j': (0, 0, 0, 1),
    'l': (0, 0, 0, -1),
    'u': (diag, diag, 0, 0),
    'k': (-1, 0, 0, 0),
    '.': (-1, 0, 0, 1),
    'm': (-1, 0, 0, -1),
    'O': (1, 1, 0, 0),
    'I': (1, 0, 0, 0),
    'J': (0, 1, 0, 0),
    'L': (0, -1, 0, 0),
    'U': (1, -1, 0, 0),
    'K': (-1, 0, 0, 0),
    '>': (-1, -1, 0, 0),
    'M': (-1, 1, 0, 0),
    't': (0, 0, 1, 0),
    'b': (0, 0, -1, 0),
    ' ': (0, 0, 0, 0),
    'h': (0, 1, 0, 0),
    ';': (0, -1, 0, 0),
}

# speed keys
speedBindings = {
    'q': (1.1, 1.1),
    'z': (.9, .9),
    'w': (1.1, 1),
    'x': (.9, 1),
    'e': (1, 1.1),
    'c': (1, .9),
}


def getKey(settings):
    if sys.platform == 'win32':
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def vels(speed, turn):
    return f'currently:\tspeed {speed}\tturn {turn}'


def rotate_180(pub, twist_msg, twist, angular_speed, stamped, node, rate_hz=20.0):
    """
    Rotate in-place 180 degrees (pi radians) using open-loop timing.
    angular_speed: positive scalar in rad/s (we rotate CCW). If 0, fallback to 1.0.
    """
    if angular_speed == 0:
        angular_speed = 1.0
    duration = math.pi / abs(angular_speed)  # seconds to rotate pi radians
    dt = 1.0 / rate_hz
    end_time = time.time() + duration

    while time.time() < end_time:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist.linear.x = twist.linear.y = twist.linear.z = 0.0
        twist.angular.x = twist.angular.y = 0.0
        twist.angular.z = angular_speed  # CCW rotation
        pub.publish(twist_msg)
        time.sleep(dt)

    # stop rotation
    if stamped:
        twist_msg.header.stamp = node.get_clock().now().to_msg()
    twist.angular.z = 0.0
    pub.publish(twist_msg)


def main():
    settings = saveTerminalSettings()

    rclpy.init()
    node = rclpy.create_node('teleop_twist_keyboard')

    # parameters
    stamped = node.declare_parameter('stamped', False).value
    frame_id = node.declare_parameter('frame_id', '').value
    if not stamped and frame_id:
        raise Exception("'frame_id' can only be set when 'stamped' is True")

    TwistMsg = geometry_msgs.msg.TwistStamped if stamped else geometry_msgs.msg.Twist

    pub = node.create_publisher(TwistMsg, 'cmd_vel', 10)

    spinner = threading.Thread(target=rclpy.spin, args=(node,))
    spinner.start()

    speed = 0.5
    turn = 1.0
    x = y = z = th = 0.0
    status = 0

    twist_msg = TwistMsg()
    if stamped:
        twist = twist_msg.twist
        twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist_msg.header.frame_id = frame_id
    else:
        twist = twist_msg

    try:
        print(msg)
        print(vels(speed, turn))
        while True:
            key = getKey(settings)

            # special 180° rotate on 't'
            if key == 't':
                angular_speed = turn if turn != 0 else 1.0
                rotate_180(pub, twist_msg, twist, angular_speed, stamped, node)
                continue

            if key in moveBindings:
                x, y, z, th = moveBindings[key]
            elif key in speedBindings:
                speed *= speedBindings[key][0]
                turn *= speedBindings[key][1]
                print(vels(speed, turn))
                status = (status + 1) % 15
            else:
                x = y = z = th = 0.0
                if key == '\x03':  # Ctrl-C
                    break

            if stamped:
                twist_msg.header.stamp = node.get_clock().now().to_msg()

            twist.linear.x = x * speed
            twist.linear.y = y * speed
            twist.linear.z = z * speed
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = th * turn
            pub.publish(twist_msg)

    except Exception as e:
        print(e)

    finally:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist.linear.x = twist.linear.y = twist.linear.z = 0.0
        twist.angular.x = twist.angular.y = twist.angular.z = 0.0
        pub.publish(twist_msg)
        rclpy.shutdown()
        spinner.join()
        restoreTerminalSettings(settings)


if __name__ == '__main__':
    main()

            # special 180° rotate on 't'
            if key == 't':
                angular_speed = turn if turn != 0 else 1.0
                rotate_180(pub, twist_msg, twist, angular_speed, stamped, node)
                continue

            if key in moveBindings:
                x, y, z, th = moveBindings[key]
            elif key in speedBindings:
                speed *= speedBindings[key][0]
                turn *= speedBindings[key][1]
                print(vels(speed, turn))
                status = (status + 1) % 15
            else:
                x = y = z = th = 0.0
                if key == '\x03':  # Ctrl-C
                    break

            if stamped:
                twist_msg.header.stamp = node.get_clock().now().to_msg()

            twist.linear.x = x * speed
            twist.linear.y = y * speed
            twist.linear.z = z * speed
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = th * turn
            pub.publish(twist_msg)

    except Exception as e:
        print(e)

    finally:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist.linear.x = twist.linear.y = twist.linear.z = 0.0
        twist.angular.x = twist.angular.y = twist.angular.z = 0.0
        pub.publish(twist_msg)
        rclpy.shutdown()
        spinner.join()
        restoreTerminalSettings(settings)


if __name__ == '__main__':
    main()
