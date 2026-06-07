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
from sensor_msgs.msg import Imu, JointState, LaserScan, Image

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
        # Add camera manually since it wasn't in the config dictionary
        self.message_counts['camera'] = 0

        # Publicador para Simulink (El filtro)
        self.simulink_odom_pub = self.create_publisher(
            Odometry, '/simulink/odom_filtered', 10
        )

        self.create_subscription(
            Odometry,
            SIMULINK_INPUT_TOPICS['odom'].name,
            self._odom_callback,
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
        self.create_subscription(
            Image,
            '/camera/image_raw',
            self._store_message('camera'),
            10,
        )

        if enable_ground_truth:
            self.create_subscription(
                PoseStamped,
                SIMULINK_INPUT_TOPICS['ground_truth_pose'].name,
                self._store_message('ground_truth_pose'),
                10,
            )

        self.create_timer(1.0, self._log_status)  # Imprimir cada segundo
        self.get_logger().info('ROS to Simulink bridge ready. Processing sensors...')

    def _store_message(self, key):
        def callback(message):
            self.latest_messages[key] = message
            self.message_counts[key] += 1

        return callback

    def _odom_callback(self, message):
        # Guardar para el logger
        self.latest_messages['odom'] = message
        self.message_counts['odom'] += 1
        
        # Opcionalmente procesar aquí. Por ahora, reenviamos tal cual a Simulink
        self.simulink_odom_pub.publish(message)

    def _log_status(self):
        # Imprimir datos de los sensores de forma tangible
        odom_msg = self.latest_messages.get('odom')
        scan_msg = self.latest_messages.get('scan')
        cam_msg = self.latest_messages.get('camera')

        if odom_msg and scan_msg:
            x_pos = odom_msg.pose.pose.position.x
            # Buscar el obstáculo más cercano
            min_dist = min([d for d in scan_msg.ranges if d > 0.0], default=float('inf'))
            cam_status = "OK" if cam_msg else "No Data"
            
            self.get_logger().info(
                f'Sensor Data -> Odom X: {x_pos:.2f} m | Lidar Min Dist: {min_dist:.2f} m | Cam: {cam_status}'
            )
        else:
            self.get_logger().info('Waiting for sensor data from Gazebo...')


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
