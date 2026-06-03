"""Base ROS 2 command bridge for future Simulink co-simulation.

The current architecture allows MATLAB or Simulink to publish directly to
/cmd_vel. This node is therefore disabled by default so it cannot accidentally
compete with a future external controller.
"""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node

from robot_control.interfaces.topic_config import SIMULINK_OUTPUT_TOPICS


class SimulinkToRosBridge(Node):
    """Optional forwarder from a private Simulink topic to /cmd_vel."""

    def __init__(self):
        super().__init__('simulink_to_ros_bridge')

        self.declare_parameter('enable_forwarding', False)
        self.declare_parameter('input_topic', '/simulink/cmd_vel')
        self.declare_parameter(
            'output_topic',
            SIMULINK_OUTPUT_TOPICS['cmd_vel'].name,
        )

        self.enable_forwarding = (
            self.get_parameter('enable_forwarding')
            .get_parameter_value()
            .bool_value
        )
        self.input_topic = (
            self.get_parameter('input_topic')
            .get_parameter_value()
            .string_value
        )
        self.output_topic = (
            self.get_parameter('output_topic')
            .get_parameter_value()
            .string_value
        )

        if not self.enable_forwarding:
            self.get_logger().info(
                'Simulink command bridge is inactive. Publish directly to /cmd_vel '
                'or set enable_forwarding:=true when a private input topic is needed.'
            )
            return

        self.publisher = self.create_publisher(Twist, self.output_topic, 10)
        self.subscription = self.create_subscription(
            Twist,
            self.input_topic,
            self._forward_command,
            10,
        )
        self.get_logger().info(
            f'Forwarding Twist commands from {self.input_topic} to {self.output_topic}.'
        )

    def _forward_command(self, message):
        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = SimulinkToRosBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
