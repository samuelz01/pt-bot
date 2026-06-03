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

    archivo_mundo = os.path.join(dir_paquete, 'worlds', 'mundo_vacio.sdf')
    archivo_modelo = os.path.join(dir_modelos, 'nuevo_carro', 'model.sdf')
    archivo_topicos = os.path.join(dir_paquete, 'config', 'topics.yaml')

    mundo = LaunchConfiguration('world')
    argumentos_gz = LaunchConfiguration('gz_args')

    argumento_mundo = DeclareLaunchArgument(
        'world',
        default_value=archivo_mundo,
        description='Mundo vacio para pruebas del carro mecanum',
    )
    argumento_gz = DeclareLaunchArgument(
        'gz_args',
        default_value='-r',
        description='Argumentos para Gazebo Sim; usa "-r -s" para modo servidor',
    )
    argumento_topicos = DeclareLaunchArgument(
        'topic_config',
        default_value=archivo_topicos,
        description='Mapa documentado de topics ROS 2 para Simulink',
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
    topico_joint_state_gz = (
        '/world/mundo_vacio/model/mecanum_bot/joint_state'
    )

    puente = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='puente_sim_empty_world',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            f'{topico_gz}/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            f'{topico_gz}/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            f'{topico_joint_state_gz}@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        remappings=[
            (f'{topico_gz}/cmd_vel', '/cmd_vel'),
            (f'{topico_gz}/odometry', '/odom'),
            (topico_joint_state_gz, '/joint_states'),
            ('/camera/image', '/camera/image_raw'),
        ],
        output='screen',
    )

    ros_to_simulink = Node(
        package='robot_control',
        executable='ros_to_simulink_bridge',
        name='ros_to_simulink_bridge',
        output='screen',
    )

    simulink_to_ros = Node(
        package='robot_control',
        executable='simulink_to_ros_bridge',
        name='simulink_to_ros_bridge',
        parameters=[{'enable_forwarding': False}],
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
        argumento_topicos,
        simulador,
        crear_robot,
        puente,
        ros_to_simulink,
        simulink_to_ros,
    ])
