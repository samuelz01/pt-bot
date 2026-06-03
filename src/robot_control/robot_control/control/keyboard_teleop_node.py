import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


LINEAR_SPEED = 0.6
ANGULAR_SPEED = 1.0
CMD_VEL_TOPIC = '/cmd_vel'
STOP_REPEATS = 3
STOP_INTERVAL_SECONDS = 0.05


class KeyboardTeleop(Node):
    """Simple keyboard teleoperation node for the Gazebo mecanum car."""

    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher = self.create_publisher(Twist, CMD_VEL_TOPIC, 10)

    def publish_command(self, linear_x=0.0, angular_z=0.0):
        message = Twist()
        message.linear.x = float(linear_x)
        message.angular.z = float(angular_z)
        self.publisher.publish(message)

    def stop_robot(self):
        for _ in range(STOP_REPEATS):
            self.publish_command(0.0, 0.0)
            time.sleep(STOP_INTERVAL_SECONDS)


def read_key():
    if not select.select([sys.stdin], [], [], 0.1)[0]:
        return ''

    key = sys.stdin.read(1)
    if key == '\x1b':
        key += sys.stdin.read(2)
    return key


def print_controls():
    print('')
    print('Keyboard teleop para /cmd_vel')
    print('Flecha arriba    : avanzar')
    print('Flecha abajo     : retroceder')
    print('Flecha izquierda : girar izquierda')
    print('Flecha derecha   : girar derecha')
    print('Espacio          : detener')
    print('q                : salir')
    print('')


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()

    if not sys.stdin.isatty():
        node.get_logger().error('keyboard_teleop requiere una terminal interactiva.')
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()
        return

    original_settings = termios.tcgetattr(sys.stdin)
    should_quit = False

    try:
        tty.setcbreak(sys.stdin.fileno())
        print_controls()

        while rclpy.ok() and not should_quit:
            rclpy.spin_once(node, timeout_sec=0.0)
            key = read_key()

            if key == '\x1b[A':
                node.publish_command(linear_x=LINEAR_SPEED)
            elif key == '\x1b[B':
                node.publish_command(linear_x=-LINEAR_SPEED)
            elif key == '\x1b[D':
                node.publish_command(angular_z=ANGULAR_SPEED)
            elif key == '\x1b[C':
                node.publish_command(angular_z=-ANGULAR_SPEED)
            elif key == ' ':
                node.stop_robot()
            elif key.lower() == 'q':
                should_quit = True

        node.stop_robot()
    except KeyboardInterrupt:
        node.stop_robot()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
