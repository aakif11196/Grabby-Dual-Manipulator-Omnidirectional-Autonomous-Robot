import os
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Get package paths
    axebot_description_path = get_package_share_directory('axebot_description')
    
    # Process xacro file directly in Python
    xacro_file = os.path.join(axebot_description_path, 'urdf', 'axebot.urdf.xacro')
    doc = xacro.process_file(xacro_file)
    robot_description_config = doc.toxml()

    # 1. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': ParameterValue(robot_description_config, value_type=str)}]
    )

    # 2. RViz Visualization
    rviz_config_file = os.path.join(axebot_description_path, 'config', 'axebot.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    # 3. Digital Twin Nodes (Right Arm)
    right_serial_reader = Node(
        package='axebot_control',
        executable='universal_serial_reader.py',
        name='right_serial_reader',
        output='screen',
        parameters=[{
            'port': '/dev/ttyACM0',
            'topic_name': 'joint_commands_right',
            'min_angle': -2.356,
            'max_angle': 2.356
        }]
    )

    right_arm_bridge = Node(
        package='axebot_control',
        executable='universal_arm_controller.py',
        name='right_arm_bridge',
        output='screen',
        parameters=[{
            'input_topic': 'joint_commands_right',
            'arm_prefix': 'vx300s_right',
            'output_joint_state_topic': '/right_arm_joint_states'
        }]
    )

    # 3. Digital Twin Nodes (Left Arm)
    left_serial_reader = Node(
        package='axebot_control',
        executable='universal_serial_reader.py',
        name='left_serial_reader',
        output='screen',
        parameters=[{
            'port': '/dev/ttyUSB0',
            'topic_name': 'joint_commands_left',
            'min_angle': -2.356,
            'max_angle': 2.356
        }]
    )

    left_arm_bridge = Node(
        package='axebot_control',
        executable='universal_arm_controller.py',
        name='left_arm_bridge',
        output='screen',
        parameters=[{
            'input_topic': 'joint_commands_left',
            'arm_prefix': 'vx300s_left',
            'output_joint_state_topic': '/left_arm_joint_states'
        }]
    )

    # 4. Joint State Publisher (Merges static joints + arm_joint_states)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'source_list': ['/right_arm_joint_states', '/left_arm_joint_states']}]
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz_node,
        right_serial_reader,
        right_arm_bridge,
        left_serial_reader,
        left_arm_bridge
    ])