import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'robot_control'
    pkg_share = get_package_share_directory(pkg_name)
    
    xacro_file = os.path.join(pkg_share, 'urdf', 'tricycle.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_desc = robot_description_config.toxml()
    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )
    
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    gz_launch_file = os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
    
    # 4. Incluir el laucher del "Nuevo Gazebo" y cargar nuestro circuito personalizado
    world_file = os.path.join(pkg_share, 'worlds', 'line_follower.sdf')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch_file),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )
    
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'tricycle_bot',
                   '-z', '0.1'], # Caída segura sin forzar banderas conflictivas X/Y
        output='screen'
    )

    # 5. Puente de variables entre ROS 2 y Gazebo Harmonic
    # Toma mensajes Twist de ROS 2 y los traduce al formato de red interna de Gazebo
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image'
        ],
        output='screen'
    )
    
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
        bridge
    ])
