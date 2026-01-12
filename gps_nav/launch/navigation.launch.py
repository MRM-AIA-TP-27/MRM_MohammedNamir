import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    # Package name
    package_name = 'gps_nav'

    # Dynamically find the URDF path in the install directory
    urdf_path = os.path.join(
        get_package_share_directory(package_name),
        'urdf',
        'rover.urdf'
    )

    # Read the URDF file content
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # Robot State Publisher (Publishes robot_description topic)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),

        # Spawn Entity in Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-topic', 'robot_description', '-entity', 'basic_rover'],
            output='screen'
        ),

        # GPS Navigation Node
        Node(
            package=package_name,
            executable='gps_navigator',
            name='gps_navigator',
            output='screen'
        ),

        # Gazebo Simulation
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        )
    ])
