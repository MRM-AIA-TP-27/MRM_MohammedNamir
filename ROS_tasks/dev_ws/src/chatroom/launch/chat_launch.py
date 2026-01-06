from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # List of 3 users to simulate the chatroom
    users = ['User_A', 'User_B', 'User_C']
    nodes = []

    for user in users:
        nodes.append(
            Node(
                package='chatroom',
                executable='chat_node',
                name=user,
                output='screen',
                prefix="gnome-terminal --" # Opens each node in a new terminal window
            )
        )
    return LaunchDescription(nodes)
