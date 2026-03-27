import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # --- 0. LAUNCH ARGUMENTS ---
    min_angle_arg = DeclareLaunchArgument('min_angle', default_value='-2.356', description='Minimum angle for joints')
    max_angle_arg = DeclareLaunchArgument('max_angle', default_value='2.356', description='Maximum angle for joints')
    use_gui_arg = DeclareLaunchArgument('use_gui', default_value='false', description='Use Joint State Publisher GUI')
    use_sim_arg = DeclareLaunchArgument('use_sim', default_value='false', description='Use simulation mode (no hardware, sim time)')

    min_angle = LaunchConfiguration('min_angle')
    max_angle = LaunchConfiguration('max_angle')
    use_gui = LaunchConfiguration('use_gui')
    use_sim = LaunchConfiguration('use_sim')

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
        parameters=[robot_description, {'use_sim_time': use_sim}]
    )

    # --- 3. RVIZ VISUALIZATION ---
    # Select config based on use_sim
    rviz_config_hw = os.path.join(axebot_desc_path, 'config', 'axebot.rviz')
    rviz_config_sim = os.path.join(axebot_desc_path, 'config', 'axebot_sim.rviz')
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_hw],
        condition=UnlessCondition(use_sim),
        parameters=[{'use_sim_time': False}]
    )

    rviz_node_sim = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_sim],
        condition=IfCondition(use_sim),
        parameters=[{'use_sim_time': True}]
    )

    # --- 4. DIGITAL TWIN HARDWARE NODES (Teleop) ---
    # Only launch if NOT using simulation
    
    # Right Arm Hardware
    right_serial_reader = Node(
        package='axebot_control',
        executable='universal_serial_reader.py',
        name='right_serial_reader',
        condition=UnlessCondition(use_sim),
        parameters=[{
            'port': '/dev/ttyACM0', 
            'topic_name': 'joint_commands_right',
            'min_angle': min_angle,
            'max_angle': max_angle
        }]
    )
    
    right_arm_bridge = Node(
        package='axebot_control',
        executable='universal_arm_controller.py',
        name='right_arm_bridge',
        condition=UnlessCondition(use_sim),
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
        condition=UnlessCondition(use_sim),
        parameters=[{
            'port': '/dev/ttyUSB0', 
            'topic_name': 'joint_commands_left',
            'min_angle': min_angle,
            'max_angle': max_angle
        }]
    )
    
    left_arm_bridge = Node(
        package='axebot_control',
        executable='universal_arm_controller.py',
        name='left_arm_bridge',
        condition=UnlessCondition(use_sim),
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
        condition=UnlessCondition(use_gui),
        parameters=[{'source_list': ['/right_arm_joint_states', '/left_arm_joint_states'], 'use_sim_time': use_sim}]
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(use_gui),
        parameters=[{'source_list': ['/right_arm_joint_states', '/left_arm_joint_states'], 'use_sim_time': use_sim}]
    )

    # --- 6. RETURN DESCRIPTION ---
    return LaunchDescription([
        min_angle_arg,
        max_angle_arg,
        use_gui_arg,
        use_sim_arg,
        robot_state_publisher,
        rviz_node,
        rviz_node_sim,
        joint_state_publisher,
        joint_state_publisher_gui,
        right_serial_reader,
        right_arm_bridge,
        left_serial_reader,
        left_arm_bridge,
    ])