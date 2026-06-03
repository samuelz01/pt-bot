# Proyecto ROS 2 Jazzy + Gazebo + MATLAB/Simulink

Base limpia para simulacion y co-simulacion de un carro mecanum en Gazebo con
ROS 2 Jazzy.

## Arquitectura preparada

```text
Gazebo -> ROS 2 topics -> MATLAB/Simulink -> ROS 2 /cmd_vel -> carro en Gazebo
```

Fase futura:

```text
Sensores/Odometria -> estimador adaptativo -> controlador -> /cmd_vel
```

No hay implementacion completa de Simulink ni red neuronal en esta fase. Solo
queda la base modular para integrarlas despues.

## Estructura del proyecto

```text
Ros/
├── container/
├── docs/
├── matlab_integration/
│   ├── scripts/
│   ├── simulink/
│   └── README.md
├── src/
│   └── robot_control/
│       ├── launch/
│       │   ├── sim_car.launch.py
│       │   └── sim_empty_world.launch.py
│       ├── worlds/
│       │   ├── nuevo_mundo.sdf
│       │   └── mundo_vacio.sdf
│       ├── models/
│       │   ├── nuevo_carro/
│       │   └── osrf/
│       ├── config/
│       ├── robot_control/
│       │   ├── control/
│       │   │   └── keyboard_teleop_node.py
│       │   ├── sensors/
│       │   ├── interfaces/
│       │   └── utils/
│       ├── package.xml
│       └── setup.py
├── README.md
└── .gitignore
```

- `container/`: scripts para construir y manejar el entorno del contenedor ROS 2/Gazebo.
- `docs/`: documentacion tecnica del proyecto.
- `matlab_integration/`: base para futura integracion con MATLAB/Simulink.
- `src/robot_control/`: paquete principal ROS 2.
- `launch/`: archivos para lanzar mundos, robot y nodos.
- `worlds/`: mundos SDF de Gazebo.
- `models/`: modelos del robot y recursos de simulacion.
- `config/`: archivos de configuracion.
- `robot_control/control/`: nodos o modulos de control.
- `robot_control/sensors/`: sensores y procesamiento de datos.
- `robot_control/interfaces/`: futura comunicacion ROS 2 con Simulink.
- `robot_control/utils/`: funciones auxiliares.

## Comando principal

```bash
ros2-sim
```

Equivalente dentro del contenedor:

```bash
cd /root/Ros
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch robot_control sim_car.launch.py
```

Mundo vacio de pruebas:

```bash
ros2 launch robot_control sim_empty_world.launch.py
```

Teleoperacion por teclado:

```bash
ros2 run robot_control keyboard_teleop
```

## Compilacion

Desde Fedora:

```bash
cd ~/Documentos/Ros
bash container/rebuild.sh
```

Dentro del contenedor:

```bash
cd /root/Ros
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Topics principales

Entradas hacia MATLAB/Simulink:

- `/odom`
- `/scan`
- `/imu`
- `/joint_states`
- `/ground_truth_pose` opcional

Salida de MATLAB/Simulink:

- `/cmd_vel`

## Modulos base

- `robot_control/interfaces/ros_to_simulink_bridge.py`
- `robot_control/interfaces/simulink_to_ros_bridge.py`
- `robot_control/interfaces/topic_config.py`

Estos modulos son esqueletos para organizar la comunicacion futura. El puente
de comandos esta desactivado por defecto para evitar publicar en `/cmd_vel` sin
intencion explicita.
