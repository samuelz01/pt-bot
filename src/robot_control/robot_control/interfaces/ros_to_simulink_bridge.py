"""Base ROS 2 subscriber node for future Simulink co-simulation.

For now this node only subscribes to the prepared sensor/state topics and keeps
the latest messages in memory. It does not transform data, publish commands, or
control the robot. Simulink integration can later reuse this module as the
single place where ROS input topics are managed.
"""

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState, LaserScan

from robot_control.interfaces.topic_config import SIMULINK_INPUT_TOPICS


class RosToSimulinkBridge(Node):
    """Collect the ROS topics that will be inputs to Simulink."""

    def __init__(self):
        super().__init__('ros_to_simulink_bridge')

        self.declare_parameter('enable_ground_truth_pose', False)
        enable_ground_truth = (
            self.get_parameter('enable_ground_truth_pose')
            .get_parameter_value()
            .bool_value
        )

        self.latest_messages = {}
        self.message_counts = {key: 0 for key in SIMULINK_INPUT_TOPICS}

        self.create_subscription(
            Odometry,
            SIMULINK_INPUT_TOPICS['odom'].name,
            self._store_message('odom'),
            10,
        )
        self.create_subscription(
            LaserScan,
            SIMULINK_INPUT_TOPICS['scan'].name,
            self._store_message('scan'),
            10,
        )
        self.create_subscription(
            Imu,
            SIMULINK_INPUT_TOPICS['imu'].name,
            self._store_message('imu'),
            10,
        )
        self.create_subscription(
            JointState,
            SIMULINK_INPUT_TOPICS['joint_states'].name,
            self._store_message('joint_states'),
            10,
        )

        if enable_ground_truth:
            self.create_subscription(
                PoseStamped,
                SIMULINK_INPUT_TOPICS['ground_truth_pose'].name,
                self._store_message('ground_truth_pose'),
                10,
            )

        self.create_timer(5.0, self._log_status)
        self.get_logger().info('ROS to Simulink bridge ready in passive mode.')

    def _store_message(self, key):
        def callback(message):
            self.latest_messages[key] = message
            self.message_counts[key] += 1

        return callback

    def _log_status(self):
        counts = ', '.join(
            f'{key}={count}' for key, count in sorted(self.message_counts.items())
        )
        self.get_logger().info(f'Passive topic counters: {counts}')


def main(args=None):
    rclpy.init(args=args)
    node = RosToSimulinkBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
