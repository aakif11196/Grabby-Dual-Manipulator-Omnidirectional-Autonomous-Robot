import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # --- 1. SETTINGS & PATHS ---
    axebot_desc_path = get_package_share_directory('axebot_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    
    # Xacro Processing
    xacro_file = os.path.join(axebot_desc_path, 'urdf', 'axebot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file).toxml()
    robot_description = {'robot_description': ParameterValue(robot_description_config, value_type=str)}

    # World file path
    world_file = os.path.join(axebot_desc_path, 'worlds', 'world.sdf')

    # --- 2. GAZEBO SIMULATION ---
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        # launch_arguments={'gz_args': '-r empty.sdf'}.items(),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # Spawn Robot
    #spawn_robot = Node(
       # package='ros_gz_sim',
   #     executable='create',
        #arguments=[
      #      '-name', 'axebot', 
      #      '-topic', 'robot_description', 
      #      '-x', '-1.45', 
      #      '-y', '4.55', 
      #      '-z', '0.81',
      #      '-Y', '1.570796'
      #  ],
    #)

     # Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'axebot', '-topic', 'robot_description', '-y', '-1.0', '-z', '0.5'],
    )

    # --- 3. DIGITAL TWIN NODES (Hardware Drivers) ---
    # Right Arm Node
    right_arm_node = Node(
        package='axebot_control',
        executable='universal_arm_node.py',
        name='right_arm_node',
        parameters=[{
            'port': '/dev/ttyACM0', 
            'arm_prefix': 'vx300s_right',
            'use_sim_time': True
        }]
    )

    # Left Arm Node
    left_arm_node = Node(
        package='axebot_control',
        executable='universal_arm_node.py', 
        name='left_arm_node',
        parameters=[{
            'port': '/dev/ttyUSB0', 
            'arm_prefix': 'vx300s_left',
            'use_sim_time': True
        }]
    )


    # --- 4. CONTROLLER SPAWNERS (Delayed to allow Gazebo + ogre2 rendering to init) ---
    controller_spawners = TimerAction(
        period=10.0,
        actions=[
            # Base (timeouts needed because ogre2 gpu_lidar rendering slows sim during init)
            Node(package="controller_manager", executable="spawner", arguments=["joint_state_broadcaster", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
            Node(package="controller_manager", executable="spawner", arguments=["omnidirectional_controller", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
            # Arms
            Node(package="controller_manager", executable="spawner", arguments=["vx300s_left_arm_controller", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
            Node(package="controller_manager", executable="spawner", arguments=["vx300s_right_arm_controller", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
            # Grippers (Added based on your YAML)
            Node(package="controller_manager", executable="spawner", arguments=["vx300s_left_gripper_controller", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
            Node(package="controller_manager", executable="spawner", arguments=["vx300s_right_gripper_controller", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
            # Linear Actuators
            Node(package="controller_manager", executable="spawner", arguments=["left_actuator_controller", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
            Node(package="controller_manager", executable="spawner", arguments=["right_actuator_controller", "--switch-timeout", "60.0", "--service-call-timeout", "60.0"]),
        ]
    )

    # --- 5. GAZEBO BRIDGE (UPDATED) ---
    # Clock aur Cmd_vel dono ko bridge karna zaroori hai
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock Bridge (Zaroori hai use_sim_time ke liye)
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Cmd Vel Bridge (Base Control ke liye)
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            # Lidar Bridge
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        output='screen'
    )
    
 # --- 6. Odom TF Republisher (custom fix for empty frame_id & extrapolation errors) ---
    # Publishes odom->base_link TF at 50 Hz, stamping slightly into the future
    odom_tf_node = Node(
        package='axebot_control',
        executable='odom_tf_publisher.py',
        name='odom_tf_publisher',
        output='screen'
    )

    # --- 7. CMD_VEL RELAY ---
    # Relay /cmd_vel (nav2 output) -> /omnidirectional_controller/cmd_vel_unstamped
    cmd_vel_relay = Node(
        package='axebot_control',
        executable='cmd_vel_relay.py',
        name='cmd_vel_relay',
        output='screen'
    )

 #RVIZ (for map/SLAM visualization) 
    rviz_config = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
    )
    
    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        gz_bridge,
        right_arm_node,
        left_arm_node,
        controller_spawners,
        rviz_node,
        odom_tf_node,
        cmd_vel_relay,
    ])
