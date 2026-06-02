# 🤖 Robot Seguidor de Línea — ROS 2 Jazzy + Gazebo Harmonic

Robot autónomo seguidor de línea negra con detección de meta roja, implementado en **ROS 2 Jazzy**, **Gazebo Harmonic** y **visión por computadora (OpenCV)**.

## 1. Arquitectura del Sistema

El proyecto utiliza un contenedor aislado para la simulación y ROS 2, pero permite control nativo desde Fedora a través de DDS.

```text
Host Fedora (MATLAB) <---- DDS sobre red local ----> Contenedor Ubuntu (ROS 2 + Gazebo)
```

## 2. Estructura del Proyecto

Se ha separado de forma estricta el código fuente, la integración externa y las herramientas del contenedor:

```text
~/Documentos/Ros/
├── src/                          # Código fuente ROS 2 (paquete robot_control)
│   └── robot_control/
│       ├── launch/               # Launch files de Gazebo
│       ├── models/               # Robot mecanum y assets de mundos
│       ├── urdf/                 # Modelo funcional original
│       └── worlds/               # Mundos de simulación
├── matlab_integration/           # Control externo con MATLAB
│   ├── demo_line_follower.m      # MAIN DEMO: Control autónomo
│   ├── diagnostico_conexion.m    # Herramienta de red DDS
│   └── monitor_velocidad.m       # Gráficas en tiempo real
├── container/                    # Configuración del contenedor Podman
│   ├── ros2_jazzy_fedora.sh      # Instalador y creador del contenedor
│   ├── fix_xauth.sh              # Inyector de permisos X11 para GUI de Gazebo
│   └── rebuild.sh                # Script de compilación (wrapper de colcon)
├── README.md                     # Esta documentación
└── .gitignore                    # Reglas para Git
```

## 3. Instalación

Ejecuta el script del contenedor para configurar todo automáticamente:
```bash
cd ~/Documentos/Ros
bash container/ros2_jazzy_fedora.sh
source ~/.bashrc
```

## 4. Compilación

Si modificas archivos en `src/`, debes recompilar el proyecto. Hemos incluido un script en la carpeta `container/` para hacerlo desde el host sin necesidad de entrar al contenedor:

```bash
bash container/rebuild.sh
```

## 5. Ejecución del Proyecto

### Modo A: Seguidor Nativo en ROS 2 (Python)
1. Terminal 1: Abre la simulación con `ros2-sim`
2. Terminal 2: Inicia el controlador interno con `ros2-follower`

### Modo B: Control Externo desde MATLAB
1. Terminal 1: Abre la simulación con `ros2-sim`
2. Host: Abre MATLAB y ejecuta `matlab_integration/demo_line_follower.m`

> **ADVERTENCIA:** ¡No ejecutes el Modo A y el Modo B simultáneamente! Ambos compiten por publicar en `/cmd_vel` y el robot oscilará violentamente.

### Modo C: Nuevo Modelo Mecanum en Gazebo
El nuevo robot está integrado dentro de `src/robot_control/models/nuevo_modelo/`.

Terminal 1:
```bash
podman exec -it ros2_jazzy bash -lc 'export DISPLAY=:0; export XAUTHORITY=/root/.Xauthority; export QT_QPA_PLATFORM=xcb; export QT_X11_NO_MITSHM=1; unset WAYLAND_DISPLAY; source /opt/ros/jazzy/setup.bash; source /root/Ros/install/setup.bash; ros2 launch robot_control sim_mecanum_launch.py'
```

Terminal 2:
```bash
podman exec -it ros2_jazzy bash -lc 'export DISPLAY=:0; export XAUTHORITY=/root/.Xauthority; export QT_QPA_PLATFORM=xcb; export QT_X11_NO_MITSHM=1; unset WAYLAND_DISPLAY; source /opt/ros/jazzy/setup.bash; source /root/Ros/install/setup.bash; ros2 run robot_control line_follower_node'
```

### Modo D: Mundo de Obstáculos ME5413
Este modo abre una arena compacta de obstáculos para teleoperación, SLAM, Nav2 o futuros nodos de evasión con LiDAR. El robot mecanum aparece dentro de la pista y conserva los topics `/cmd_vel`, `/scan`, `/odom`, `/tf` y `/camera/image_raw`.

Terminal 1:
```bash
podman exec -it ros2_jazzy bash -lc 'export DISPLAY=:0; export XAUTHORITY=/root/.Xauthority; export QT_QPA_PLATFORM=xcb; export QT_X11_NO_MITSHM=1; export LIBGL_ALWAYS_SOFTWARE=1; unset WAYLAND_DISPLAY; source /opt/ros/jazzy/setup.bash; source /root/Ros/install/setup.bash; ros2 launch robot_control me5413_obstacle_world_launch.py'
```

Terminal 2:
```bash
podman exec -it ros2_jazzy bash -lc 'source /opt/ros/jazzy/setup.bash; source /root/Ros/install/setup.bash; ros2 topic list | sort | grep -E "^/cmd_vel$|^/scan$|^/odom$|^/tf$|^/camera/image_raw$"'
```

Prueba rapida de movimiento:
```bash
podman exec -it ros2_jazzy bash -lc 'source /opt/ros/jazzy/setup.bash; source /root/Ros/install/setup.bash; ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.15}, angular: {z: 0.0}}" --once'
```

## 6. Utilidades del Contenedor (`container/`)

Esta carpeta aísla los scripts operativos del host:
- **`fix_xauth.sh`**: Transfiere de forma segura las credenciales de Wayland/X11 (`.Xauthority`) hacia el contenedor. Es invocado automáticamente por el alias `ros2-sim`.
- **`rebuild.sh`**: Lanza de forma transparente `colcon build` dentro de Podman.
- **`ros2_jazzy_fedora.sh`**: Orquesta todo el despliegue del proyecto.
