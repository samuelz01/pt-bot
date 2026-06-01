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
            lista_archivos = [os.path.join(raiz, archivo) for archivo in archivos]
            archivos_datos.append((ruta_destino, lista_archivos))
    return archivos_datos


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Aquí le indicamos a ROS que copie la carpeta launch durante la compilación
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        # Incluir la carpeta urdf
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*.xacro'))),
        # Incluir los mundos de simulación
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.sdf')))
    ] + obtener_archivos_recursivos('models'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='saul_rovelo',
    maintainer_email='saul_rovelo@todo.todo',
    description='Practica de comunicacion entre nodos ROS 2 con secuencia fija',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'commander_node = robot_control.commander_node:main',
            'controller_node = robot_control.controller_node:main',
            'monitor_node = robot_control.monitor_node:main',
            'line_follower_node = robot_control.line_follower_node:main',
        ],
    },
)
