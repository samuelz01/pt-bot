#!/usr/bin/env python3

"""Simulink Router Node para co-simulación.

Este nodo unifica la recolección de sensores (Odometría, Lidar, Cámara),
imprime los datos en pantalla de forma limpia y sirve como puente bidireccional
exclusivo para Simulink.
"""

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan

from robot_control.interfaces.topic_config import SIMULINK_INPUT_TOPICS, SIMULINK_OUTPUT_TOPICS


class SimulinkRouterNode(Node):
    def __init__(self):
        super().__init__('simulink_router')

        self.latest_messages = {}

        # PUBLICADORES
        # 1. Odometría hacia Simulink
        self.simulink_odom_pub = self.create_publisher(
            Odometry, '/simulink/odom_filtered', 10
        )
        # 2. Comandos hacia Gazebo
        self.gazebo_cmd_vel_pub = self.create_publisher(
            Twist, SIMULINK_OUTPUT_TOPICS['cmd_vel'].name, 10
        )

        # SUSCRIPTORES DESDE GAZEBO
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
            Image,
            '/camera/image_raw',
            self._store_message('camera'),
            10,
        )

        # SUSCRIPTOR DESDE SIMULINK
        self.create_subscription(
            Twist,
            '/simulink/cmd_vel',
            self._simulink_cmd_callback,
            10,
        )

        self.create_timer(1.0, self._log_status)
        self.get_logger().info('Simulink Router Node iniciado.')
        self.get_logger().info('Esperando datos de Gazebo...')

    def _store_message(self, key):
        def callback(message):
            self.latest_messages[key] = message
        return callback

    def _odom_callback(self, message):
        self.latest_messages['odom'] = message
        # Filtro/Puente: Reenviar odometría hacia Simulink
        self.simulink_odom_pub.publish(message)

    def _simulink_cmd_callback(self, message):
        # Puente inverso: Reenviar comandos de Simulink hacia Gazebo
        self.gazebo_cmd_vel_pub.publish(message)

    def _log_status(self):
        odom_msg = self.latest_messages.get('odom')
        scan_msg = self.latest_messages.get('scan')
        cam_msg = self.latest_messages.get('camera')

        if odom_msg and scan_msg:
            x_pos = odom_msg.pose.pose.position.x
            y_pos = odom_msg.pose.pose.position.y
            min_dist = min([d for d in scan_msg.ranges if d > 0.0], default=float('inf'))
            cam_status = "OK" if cam_msg else "No Data"
            
            self.get_logger().info(
                f'Estado -> Pos: [{x_pos:.2f}, {y_pos:.2f}] | LiDAR Min: {min_dist:.2f}m | Cámara: {cam_status}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = SimulinkRouterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
