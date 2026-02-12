import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Setup paths
    pkg_share = get_package_share_directory('gps_nav')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    urdf_file = os.path.join(pkg_share, 'urdf', 'rover.urdf')

    # Read URDF content
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    return LaunchDescription([
        # 1. Start Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
            )
        ),

        # 2. Spawn Robot
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'my_robot', '-file', urdf_file, '-z', '0.2'],
            output='screen'
        ),

        # 3. Robot State Publisher (Static Transforms)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
        ),

        # 4. Joint State Publisher (Dynamic Wheel States)
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            parameters=[{'use_sim_time': True}]
        ),

        # 5. RTAB-Map SLAM Node
        Node(
            package='rtabmap_slam', executable='rtabmap', name='rtabmap',
            parameters=[{
                'frame_id': 'base_footprint',
                'subscribe_depth': True,
                'subscribe_rgb': True,
                'approx_sync': True,
                'queue_size': 50,
                'use_sim_time': True,
                'database_path': '~/.ros/rtabmap.db',
            }],
            remappings=[
                ('rgb/image', '/d430/color/image_raw'),
                ('rgb/camera_info', '/d430/camera_info'),
                ('depth/image', '/d430/depth/image_rect_raw'),
                ('odom', '/odom')
            ],
            output='screen'
        ),

        # 6. Start RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            parameters=[{'use_sim_time': True}],
            output='screen'
        )
    ])
