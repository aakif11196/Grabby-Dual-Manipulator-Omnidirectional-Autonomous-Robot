import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Settings & Paths
    axebot_desc_path = get_package_share_directory('axebot_description')
    rviz_config = os.path.join(axebot_desc_path, 'config', 'axebot_sim.rviz')

    # RViz Node with use_sim_time=True
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        rviz_node
    ])
