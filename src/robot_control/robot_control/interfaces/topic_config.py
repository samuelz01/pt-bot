"""Central topic map for the future ROS 2 <-> Simulink interface.

This module intentionally keeps only names and message types. It does not
start nodes, publish commands, or change the current /cmd_vel behavior.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicSpec:
    """Description of a ROS 2 topic used by the simulation interface."""

    name: str
    ros_type: str
    direction: str
    required: bool
    description: str


SIMULINK_INPUT_TOPICS = {
    'odom': TopicSpec(
        name='/odom',
        ros_type='nav_msgs/msg/Odometry',
        direction='ros_to_simulink',
        required=True,
        description='Robot odometry from Gazebo, remapped from the mecanum model.',
    ),
    'scan': TopicSpec(
        name='/scan',
        ros_type='sensor_msgs/msg/LaserScan',
        direction='ros_to_simulink',
        required=True,
        description='2D lidar scan from the new car.',
    ),
    'imu': TopicSpec(
        name='/imu',
        ros_type='sensor_msgs/msg/Imu',
        direction='ros_to_simulink',
        required=True,
        description='IMU data from the new car.',
    ),
    'joint_states': TopicSpec(
        name='/joint_states',
        ros_type='sensor_msgs/msg/JointState',
        direction='ros_to_simulink',
        required=True,
        description='Wheel and joint state feedback from Gazebo.',
    ),
    'ground_truth_pose': TopicSpec(
        name='/ground_truth_pose',
        ros_type='geometry_msgs/msg/PoseStamped',
        direction='ros_to_simulink',
        required=False,
        description='Optional ground-truth pose for experiments.',
    ),
}


SIMULINK_OUTPUT_TOPICS = {
    'cmd_vel': TopicSpec(
        name='/cmd_vel',
        ros_type='geometry_msgs/msg/Twist',
        direction='simulink_to_ros',
        required=True,
        description='Velocity command consumed by the simulated robot.',
    ),
}


GAZEBO_INTERNAL_TOPICS = {
    'mecanum_cmd_vel': '/model/mecanum_bot/cmd_vel',
    'mecanum_odom': '/model/mecanum_bot/odometry',
    'mecanum_joint_state': '/world/nuevo_mundo/model/mecanum_bot/joint_state',
}


def all_topic_specs():
    """Return every configured topic spec as a single dictionary."""

    return {
        **SIMULINK_INPUT_TOPICS,
        **SIMULINK_OUTPUT_TOPICS,
    }
