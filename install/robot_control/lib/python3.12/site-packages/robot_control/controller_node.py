import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        
        # 1. Crear Suscriptor para escuchar los comandos
        self.subscription = self.create_subscription(
            String,
            '/robot_command',
            self.command_callback,
            10
        )
        
        # 2. Crear Publicador para enviar el estado a la pantalla
        self.publisher_ = self.create_publisher(
            String,
            '/robot_state',
            10
        )
        
        self.get_logger().info('Controller Node inicializado. Esperando órdenes...')

    def command_callback(self, msg):
        # 3. Recibir el comando y extraer la cadena de texto
        command = msg.data
        self.get_logger().info(f'¡Recibida la orden!: "{command}"')
        
        # 4. Simular la física o procesamiento del comando
        state_msg = String()
        
        if command == 'MOVER_ADELANTE':
            state_msg.data = 'Estado: Motores a máxima potencia, avanzando.'
        elif command == 'GIRAR_IZQUIERDA':
            state_msg.data = 'Estado: Rotando 90 grados a la izquierda.'
        elif command == 'DETENER':
            state_msg.data = 'Estado: Freno de emergencia activado, quieto.'
        else:
            state_msg.data = f'Estado: Comando desconocido "{command}".'
            
        # 5. Publicar la reacción/estado generado
        self.publisher_.publish(state_msg)
        self.get_logger().info(f'Enviando nuevo estado: {state_msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Controller Node desconectado.')
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
