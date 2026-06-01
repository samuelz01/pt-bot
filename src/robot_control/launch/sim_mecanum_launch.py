import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    dir_paquete = get_package_share_directory('robot_control')
    launch_nuevo_modelo = os.path.join(
        dir_paquete, 'launch', 'nuevo_modelo_line_follower_launch.py')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_nuevo_modelo),
        ),
    ])
