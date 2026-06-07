import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'robot_control'


def obtener_archivos_recursivos(directorio_base):
    archivos_datos = []
    for raiz, _, archivos in os.walk(directorio_base):
        if archivos:
            ruta_relativa = os.path.relpath(raiz, '.')
            ruta_destino = os.path.join('share', package_name, ruta_relativa)
            lista_archivos = [
                os.path.join(raiz, archivo)
                for archivo in archivos
                if os.path.isfile(os.path.join(raiz, archivo))
            ]
            if lista_archivos:
                archivos_datos.append((ruta_destino, lista_archivos))
    return archivos_datos


def glob_archivos_existentes(patron):
    return [ruta for ruta in glob(patron) if os.path.isfile(ruta)]


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Instalar launch files, mundos, configuracion y modelos de Gazebo.
        (os.path.join('share', package_name, 'launch'), glob_archivos_existentes(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'worlds'), glob_archivos_existentes(os.path.join('worlds', '*.sdf'))),
        (os.path.join('share', package_name, 'config'), glob_archivos_existentes(os.path.join('config', '*.yaml'))),
    ] + obtener_archivos_recursivos('models'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Samuel Perez',
    maintainer_email='samuel_perez@todo.todo',
    description='Base ROS 2/Gazebo para co-simulacion con MATLAB y Simulink',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ros_to_simulink_bridge = robot_control.interfaces.ros_to_simulink_bridge:main',
            'simulink_to_ros_bridge = robot_control.interfaces.simulink_to_ros_bridge:main',
            'keyboard_teleop = robot_control.control.keyboard_teleop_node:main',
            'simulink_router = robot_control.control.simulink_router_node:main',
        ],
    },
)
