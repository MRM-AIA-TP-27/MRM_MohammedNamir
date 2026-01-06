OS 2 Chatroom
1. Description & Approach

This package implements a multi-user chatroom in ROS 2 Humble using a Peer-to-Peer (P2P) model.

    Nodes: Every user runs a node that is both a Publisher and Subscriber.

    Logic: Each node broadcasts to a shared topic. To allow simultaneous typing and receiving, the keyboard input is handled in a separate C++ thread (std::thread) so it doesn't block the ROS executor.

2. ROS Topics

    /chat_topic (std_msgs/msg/String): The central channel for all chat communication.

3. Messages & Services

    Messages: Uses standard std_msgs/msg/String.

    Services: None used; the system relies on asynchronous Pub/Sub for real-time interaction.

4. RQT Graph

The graph shows multiple user nodes (User1, User2, User3) interacting through the /chat_topic.

5. Video Demo

YouTube Link: https://youtu.be/cI4U4TH8WPU
Setup and Execution

    Build: colcon build --packages-select chatroom

    Source: source install/setup.bash

    Run: ros2 launch chatroom chat_launch.py
