import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    nombre_paquete = 'robot_control'
    dir_paquete = get_package_share_directory(nombre_paquete)

    dir_modelos = os.path.join(dir_paquete, 'models')
    rutas = [
        dir_modelos,
        os.path.join(dir_modelos, 'osrf'),
        dir_paquete,
        os.path.dirname(dir_paquete),
    ]
    ruta_existente = os.environ.get('GZ_SIM_RESOURCE_PATH')
    if ruta_existente:
        rutas.append(ruta_existente)
    rutas_gz = os.pathsep.join(rutas)

    archivo_mundo = os.path.join(dir_paquete, 'worlds', 'me5413_obstacle_world.sdf')
    archivo_modelo = os.path.join(dir_modelos, 'nuevo_modelo', 'model.sdf')
    mundo = LaunchConfiguration('world')
    argumentos_gz = LaunchConfiguration('gz_args')

    argumento_mundo = DeclareLaunchArgument(
        'world',
        default_value=archivo_mundo,
        description='Mundo ME5413 adaptado para Gazebo Harmonic con obstaculos estaticos',
    )
    argumento_gz = DeclareLaunchArgument(
        'gz_args',
        default_value='-r',
        description='Argumentos para Gazebo Sim; usa "-r -s" para modo servidor sin GUI',
    )

    comando_gz = [
        'exec gz sim ',
        argumentos_gz,
        ' ',
        mundo,
        ' --force-version 8 2> >(grep -v "XML Element\\[gz_frame_id\\]" >&2)',
    ]
    simulador = ExecuteProcess(
        cmd=['bash', '-lc', comando_gz],
        name='gazebo',
        output='screen',
    )

    crear_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', archivo_modelo,
            '-name', 'mecanum_bot',
            '-x', '-5.0',
            '-y', '0.0',
            '-z', '0.2',
            '-Y', '0.0',
        ],
        output='screen',
    )

    topico_gz = '/model/mecanum_bot'

    puente = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='puente_me5413_obstacle_world',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            f'{topico_gz}/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            f'{topico_gz}/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            f'{topico_gz}/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        remappings=[
            (f'{topico_gz}/cmd_vel', '/cmd_vel'),
            (f'{topico_gz}/odometry', '/odom'),
            (f'{topico_gz}/tf', '/tf'),
            ('/camera/image', '/camera/image_raw'),
        ],
        output='screen',
    )

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', rutas_gz),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', rutas_gz),
        SetEnvironmentVariable('GZ_IP', '127.0.0.1'),
        SetEnvironmentVariable('IGN_IP', '127.0.0.1'),
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
        argumento_mundo,
        argumento_gz,
        simulador,
        crear_robot,
        puente,
    ])
