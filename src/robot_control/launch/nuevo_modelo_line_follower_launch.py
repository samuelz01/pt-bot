import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nombre_paquete = 'robot_control'
    dir_paquete = get_package_share_directory(nombre_paquete)

    dir_modelos = os.path.join(dir_paquete, 'models')
    dir_share = os.path.dirname(dir_paquete)
    rutas = [
        dir_modelos,
        dir_paquete,
        dir_share,
    ]
    ruta_existente = os.environ.get('GZ_SIM_RESOURCE_PATH')
    if ruta_existente:
        rutas.append(ruta_existente)
    rutas_gz = os.pathsep.join(rutas)

    archivo_mundo = os.path.join(
        dir_paquete, 'worlds', 'nuevo_modelo_line_follower.sdf')
    archivo_modelo = os.path.join(
        dir_paquete, 'models', 'nuevo_modelo', 'model.sdf')
    mundo = LaunchConfiguration('world')

    argumento_mundo = DeclareLaunchArgument(
        'world',
        default_value=archivo_mundo,
        description='Mundo SDF para lanzar el nuevo modelo mecanum seguidor de linea',
    )

    configurar_gz_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=rutas_gz,
    )
    configurar_ign_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=rutas_gz,
    )
    configurar_gz_ip = SetEnvironmentVariable(
        name='GZ_IP',
        value='127.0.0.1',
    )
    configurar_ign_ip = SetEnvironmentVariable(
        name='IGN_IP',
        value='127.0.0.1',
    )

    dir_gz_sim = get_package_share_directory('ros_gz_sim')
    archivo_lanzador_gz = os.path.join(dir_gz_sim, 'launch', 'gz_sim.launch.py')

    simulador = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(archivo_lanzador_gz),
        launch_arguments={'gz_args': ['-r ', mundo]}.items(),
    )

    crear_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', archivo_modelo,
            '-name', 'mecanum_bot',
            '-x', '0.1',
            '-y', '0.0',
            '-z', '0.1',
        ],
        output='screen',
    )

    topico_gz = '/model/mecanum_bot'

    puente = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='puente_nuevo_modelo',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            f'{topico_gz}/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            f'{topico_gz}/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        remappings=[
            (f'{topico_gz}/cmd_vel', '/cmd_vel'),
            (f'{topico_gz}/odometry', '/odom'),
            ('/camera/image', '/camera/image_raw'),
        ],
        output='screen',
    )

    return LaunchDescription([
        configurar_gz_path,
        configurar_ign_path,
        configurar_gz_ip,
        configurar_ign_ip,
        argumento_mundo,
        simulador,
        crear_robot,
        puente,
    ])
