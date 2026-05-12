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

## 6. Utilidades del Contenedor (`container/`)

Esta carpeta aísla los scripts operativos del host:
- **`fix_xauth.sh`**: Transfiere de forma segura las credenciales de Wayland/X11 (`.Xauthority`) hacia el contenedor. Es invocado automáticamente por el alias `ros2-sim`.
- **`rebuild.sh`**: Lanza de forma transparente `colcon build` dentro de Podman.
- **`ros2_jazzy_fedora.sh`**: Orquesta todo el despliegue del proyecto.
