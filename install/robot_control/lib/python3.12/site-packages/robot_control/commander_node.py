import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class CommanderNode(Node):
    def __init__(self):
        super().__init__('commander_node')
        
        # 1. Crear el publicador: (Tipo de Mensaje, Nombre del Topic, Tamaño de la cola)
        self.publisher_ = self.create_publisher(String, '/robot_command', 10)
        
        # 2. Definir la secuencia de comandos fija
        self.commands = ['MOVER_ADELANTE', 'GIRAR_IZQUIERDA', 'DETENER']
        self.current_cmd_idx = 0
        
        # 3. Crear un temporizador que ejecutará 'timer_callback' cada 2.0 segundos
        timer_period = 2.0 
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info('Commander Node inicializado. Comenzando a publicar comandos...')

    def timer_callback(self):
        # Tomar el comando actual de la secuencia
        cmd_text = self.commands[self.current_cmd_idx]
        
        # Construir el objeto de mensaje y asignarle los datos
        msg = String()
        msg.data = cmd_text
        
        # Publicar en el topic correspondiente y registrar un log
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publicando Comando: "{msg.data}"')
        
        # Preparar el siguiente ciclo usando el operador módulo (%) para repetir la lista cíclicamente
        self.current_cmd_idx = (self.current_cmd_idx + 1) % len(self.commands)


def main(args=None):
    # Iniciar la comunicación de ROS 2
    rclpy.init(args=args)
    
    # Instanciar nuestro nodo
    node = CommanderNode()
    
    try:
        # Mantener el nodo vivo en un bucle prestando atención a los callbacks
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Commander Node detenido manualmente.')
    finally:
        # Destrucciones limpias al salir
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
