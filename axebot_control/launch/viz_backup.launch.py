import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # --- 1. SETTINGS & PATHS ---
    axebot_desc_path = get_package_share_directory('axebot_description')
    
    # Xacro Processing
    xacro_file = os.path.join(axebot_desc_path, 'urdf', 'axebot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file).toxml()
    robot_description = {'robot_description': ParameterValue(robot_description_config, value_type=str)}

    # --- 2. ROBOT STATE PUBLISHER ---
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description, {'use_sim_time': False}]
    )

    # --- 3. RVIZ VISUALIZATION ---
    rviz_config = os.path.join(axebot_desc_path, 'config', 'axebot.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config]
    )

    # --- 4. DIGITAL TWIN HARDWARE NODES (Teleop) ---
    # Right Arm Hardware
    right_serial_reader = Node(
        package='axebot_control',
        executable='universal_serial_reader.py',
        name='right_serial_reader',
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
        parameters=[{
            'input_topic': 'joint_commands_right', 
            'arm_prefix': 'vx300s_right',
            'output_joint_state_topic': '/right_arm_joint_states'
        }]
    )

    # Left Arm Hardware
    left_serial_reader = Node(
        package='axebot_control',
        executable='universal_serial_reader.py',
        name='left_serial_reader',
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
        parameters=[{
            'input_topic': 'joint_commands_left', 
            'arm_prefix': 'vx300s_left',
            'output_joint_state_topic': '/left_arm_joint_states'
        }]
    )

    # --- 5. JOINT STATE PUBLISHER ---
    # Aggregates joint states from arms and static joints
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'source_list': ['/right_arm_joint_states', '/left_arm_joint_states']}]
    )

    # --- 6. RETURN DESCRIPTION ---
    return LaunchDescription([
        robot_state_publisher,
        rviz_node,
        joint_state_publisher,
        right_serial_reader,
        right_arm_bridge,
        left_serial_reader,
        left_arm_bridge,
    ])