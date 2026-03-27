import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MonitorNode(Node):
    def __init__(self):
        super().__init__('monitor_node')
        
        # 1. Crear el Suscriptor al estado del robot
        self.subscription = self.create_subscription(
            String,
            '/robot_state',
            self.state_callback,
            10
        )
        
        self.get_logger().info('Monitor Node conectado. Visualizando la telemetría del robot...')

    def state_callback(self, msg):
        # 2. Imprimir de manera limpia y clara en pantalla el mensaje recibido
        estado = msg.data
        self.get_logger().info(f'--- [DASHBOARD] --- {estado}')

def main(args=None):
    rclpy.init(args=args)
    node = MonitorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Monitor Node apagado y desconectado.')
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
