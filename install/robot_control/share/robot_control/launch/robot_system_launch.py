from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Nodo 1: El que manda las secuencias de acciones
        Node(
            package='robot_control',
            executable='commander_node',
            name='commander_node'
        ),
        # Nodo 2: El que recibe los comandos y calcula el estado
        Node(
            package='robot_control',
            executable='controller_node',
            name='controller_node'
        ),
        # Nodo 3: El que lee la telemetría y muesra el dashboard
        Node(
            package='robot_control',
            executable='monitor_node',
            name='monitor_node',
            output='screen'  # IMPORTANTE: Permite ver los prints de este nodo en consola
        )
    ])
