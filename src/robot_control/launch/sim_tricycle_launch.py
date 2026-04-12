import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # ── Rutas del paquete ───────────────────────────────────────────────
    nombre_paquete = 'robot_control'
    dir_paquete    = get_package_share_directory(nombre_paquete)

    # Procesar el modelo URDF/Xacro del robot
    archivo_xacro      = os.path.join(dir_paquete, 'urdf', 'tricycle.xacro')
    config_descripcion = xacro.process_file(archivo_xacro)
    descripcion_robot  = config_descripcion.toxml()

    # ── Nodo: Publicador del estado del robot (cinemática) ──────────────
    nodo_estado_robot = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': descripcion_robot}]
    )

    # ── Nodo: Gazebo Harmonic con el mundo personalizado ────────────────
    dir_gz_sim          = get_package_share_directory('ros_gz_sim')
    archivo_lanzador_gz = os.path.join(dir_gz_sim, 'launch', 'gz_sim.launch.py')
    archivo_mundo       = os.path.join(dir_paquete, 'worlds', 'line_follower.sdf')

    simulador = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(archivo_lanzador_gz),
        launch_arguments={'gz_args': f'-r {archivo_mundo}'}.items(),
    )

    # ── Nodo: Generar el robot en la simulación ──────────────────────────
    # Caída segura desde 0.1 m para que la física no explote al nacer
    crear_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'tricycle_bot',
                   '-z', '0.1'],
        output='screen'
    )

    # ── Nodo: Puente de mensajes ROS 2 ↔ Gazebo ─────────────────────────
    # Traduce Twist (/cmd_vel) e Image (/camera/image_raw) entre ambos mundos
    puente = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image'
        ],
        output='screen'
    )

    return LaunchDescription([
        nodo_estado_robot,
        simulador,
        crear_robot,
        puente
    ])
