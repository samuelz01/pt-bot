# 🤖 Robot Seguidor de Línea — ROS 2 Jazzy + Gazebo Harmonic

Robot autónomo seguidor de línea negra con detección de meta roja,
implementado en **ROS 2 Jazzy**, **Gazebo Harmonic** y **visión por computadora (OpenCV)**.

---

## 🖥️ Plataforma

| Componente | Versión |
|---|---|
| Host OS | Fedora 44 (o cualquier Linux moderno) |
| Contenedor | Ubuntu 24.04 (Noble) vía Podman |
| ROS | ROS 2 Jazzy Jalisco |
| Simulador | Gazebo Harmonic |
| Python | 3.12 (dentro del contenedor) |
| OpenCV | ≥ 4.8 |

> **¿Por qué contenedor?**  
> ROS 2 Jazzy tiene soporte oficial exclusivo en Ubuntu 24.04 (Noble).  
> Fedora 44 usa Python 3.14, que rompe los bindings de ROS.  
> Usamos **Podman** (ya incluido en Fedora) para un entorno limpio y aislado.

---

## 🚀 Instalación desde cero (Fedora)

### Prerrequisito único: Podman

```bash
# Verificar que Podman está instalado (ya viene en Fedora)
podman --version
```

### Instalación automática

```bash
cd ~/Documentos/Ros
bash ros2_jazzy_fedora.sh
```

El script instala en un único paso:

- Ubuntu 24.04 como contenedor Podman
- ROS 2 Jazzy Desktop completo
- Gazebo Harmonic + bridges ROS↔Gz
- OpenCV + cv_bridge + colcon
- Compila el workspace `robot_control`
- Crea alias convenientes en tu `~/.bashrc`

**Tiempo estimado: 10-20 minutos** (descarga de paquetes).

---

## ▶️ Ejecución del proyecto

Recarga tus alias una vez tras la instalación:

```bash
source ~/.bashrc
```

### Terminal 1 — Simulación Gazebo

```bash
ros2-sim
# Equivale a:
# podman exec -it ros2_jazzy bash -c \
#   "source /opt/ros/jazzy/setup.bash && \
#    source /root/ros2_ws/install/setup.bash && \
#    ros2 launch robot_control sim_tricycle_launch.py"
```

### Terminal 2 — Nodo seguidor de línea

```bash
ros2-follower
# Equivale a:
# podman exec -it ros2_jazzy bash -c \
#   "source /opt/ros/jazzy/setup.bash && \
#    source /root/ros2_ws/install/setup.bash && \
#    ros2 run robot_control line_follower_node"
```

---

## 🔍 Validación

```bash
# Ver todos los topics activos
ros2-topics

# Debe mostrar al menos:
# /cmd_vel
# /camera/image_raw

# Frecuencia de la cámara (dentro del contenedor)
ros2-shell
# Luego dentro del contenedor:
source /opt/ros/jazzy/setup.bash && source /root/ros2_ws/install/setup.bash
ros2 topic hz /camera/image_raw   # ≈ 30 Hz
ros2 topic echo /cmd_vel          # velocidad publicada por el seguidor
```

---

## 🏗️ Recompilación manual

Si modificas código fuente:

```bash
bash ~/Documentos/Ros/rebuild.sh
```

O manualmente dentro del contenedor:

```bash
ros2-shell
# Dentro del contenedor:
cd /root/ros2_ws
colcon build --packages-select robot_control --symlink-install
source install/setup.bash
```

---

## 🗂️ Estructura del proyecto

```
~/Documentos/Ros/
├── ros2_jazzy_fedora.sh     ← Instalación automática completa
├── rebuild.sh               ← Recompila el workspace
├── .gitignore
├── README.md
└── src/
    └── robot_control/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── launch/
        │   └── sim_tricycle_launch.py   ← Lanza Gazebo + bridges
        ├── robot_control/
        │   ├── __init__.py
        │   └── line_follower_node.py    ← Visión + control PD
        ├── urdf/
        │   └── tricycle.xacro           ← Modelo 3D del robot
        └── worlds/
            └── line_follower.sdf        ← Pista de simulación
```

---

## 🧠 Arquitectura del sistema

```
Gazebo Harmonic
  │
  ├─ /camera/image_raw (gz.msgs.Image)
  │      │
  │   ros_gz_bridge
  │      │
  │      └──► line_follower_node
  │               ├── OpenCV: detecta línea negra y meta roja
  │               └── Publica /cmd_vel (Twist)
  │
  └─ /cmd_vel (gz.msgs.Twist)
         │
      ros_gz_bridge
         │
         └──► Tricycle Bot (física Gazebo)
```

---

## 💡 Alias disponibles tras la instalación

| Alias | Función |
|---|---|
| `ros2-sim` | Lanza la simulación completa |
| `ros2-follower` | Ejecuta el nodo seguidor |
| `ros2-shell` | Shell interactivo dentro del contenedor |
| `ros2-topics` | Lista los topics ROS activos |
| `ros2-start` | Inicia el contenedor si está parado |

---

## 🔧 Notas importantes

- El contenedor se **monta** sobre `~/Documentos/Ros` → los cambios en el host
  se ven **inmediatamente** dentro del contenedor (sin copiar archivos).
- ROS 2 usa el **Python del sistema** del contenedor (Python 3.12 en Ubuntu 24.04).
- No uses `venv` para nodos ROS; usa directamente el Python del sistema.
- Las ventanas de OpenCV (`Vista de Suelo`, `Máscara Binaria`) se muestran en
  tu pantalla Wayland/X11 mediante forwarding del display.
- Si las ventanas no aparecen: ejecuta `xhost +local:` en el host antes de `ros2-follower`.

---

## 📦 Dependencias ROS 2 (instaladas automáticamente)

| Paquete | Propósito |
|---|---|
| `ros-jazzy-desktop` | Base completa ROS 2 Jazzy |
| `ros-jazzy-ros-gz` | Integración ROS↔Gazebo |
| `ros-jazzy-ros-gz-sim` | Nodo de simulación Gazebo |
| `ros-jazzy-ros-gz-bridge` | Bridge de mensajes bidireccional |
| `ros-jazzy-ros-gz-interfaces` | Tipos de mensajes Gazebo |
| `ros-jazzy-robot-state-publisher` | Cinemática del robot (TF) |
| `ros-jazzy-cv-bridge` | Conversión Image ROS ↔ OpenCV |
| `ros-jazzy-xacro` | Procesador URDF/Xacro |
| `ros-jazzy-sensor-msgs` | Tipos de mensajes de sensores |
| `ros-jazzy-geometry-msgs` | Tipos geométricos (Twist, etc.) |
| `ros-jazzy-teleop-twist-keyboard` | Teleoperación manual (debug) |
| `python3-opencv` | Visión por computadora |
| `python3-colcon-common-extensions` | Herramienta de compilación |