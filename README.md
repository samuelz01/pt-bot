# 🤖  ROS 2 + Gazebo

Proyecto de robot seguidor de línea usando **ROS 2 Jazzy**, **Gazebo** y **visión por computadora (OpenCV)**.

---

## Instalación

### 1. Actualizar sistema e instalar dependencias

```bash
sudo apt-get update && sudo apt-get install -y \
  ros-jazzy-desktop \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-interfaces \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-cv-bridge \
  ros-jazzy-sensor-msgs \
  ros-jazzy-geometry-msgs \
  ros-jazzy-teleop-twist-keyboard \
  python3-opencv
```
#### ROS 2 Jazzy Base
- `ros-jazzy-desktop`

#### Gazebo Harmonic + Bridges
- `ros-jazzy-ros-gz`
- `ros-jazzy-ros-gz-sim`
- `ros-jazzy-ros-gz-bridge`
- `ros-jazzy-ros-gz-interfaces`

#### Descripción y visualización del robot
- `ros-jazzy-robot-state-publisher`

#### Mensajes y tipos de datos ROS 2
- `ros-jazzy-sensor-msgs`
- `ros-jazzy-geometry-msgs`

#### Visión por computadora
- `ros-jazzy-cv-bridge`
- `python3-opencv`

#### Teleoperación (opcional, para pruebas manuales)
- `ros-jazzy-teleop-twist-keyboard`

### 2. Configurar entorno ROS de forma permanente

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 3. Verificación de instalación

```bash
echo $ROS_DISTRO
# Debe mostrar: jazzy

ros2 pkg list | grep robot_state_publisher
# Debe listar el paquete

python3 -c "import cv2; print('OpenCV OK:', cv2.__version__)"
# Debe mostrar la versión de OpenCV
```

### 4. Python utilizado

Este proyecto corre con el **Python del sistema**, por ejemplo:

```bash
python3 --version
```

En este entorno se utilizó **Python 3.12.3**.

---

## 🏗️ Compilación del proyecto

```bash

# Limpiar compilaciones anteriores
rm -rf build install log

# Cargar entorno base de ROS
source /opt/ros/jazzy/setup.bash

# Compilar el paquete
colcon build --packages-select robot_control

# Cargar el workspace compilado
source install/setup.bash
```

---

## ▶️ Ejecución

### Terminal 1: lanzar simulación

```bash
source ~/Documentos/Ros/install/setup.bash
ros2 launch robot_control sim_tricycle_launch.py
```

### Terminal 2: lanzar nodo seguidor

```bash
source ~/Documentos/Ros/install/setup.bash
ros2 run robot_control line_follower_node
```

---

## 🔍 Validación rápida

```bash
ros2 topic list
# Debe mostrar al menos:
# /cmd_vel
# /camera/image_raw

ros2 topic hz /camera/image_raw
# Debe mostrar aproximadamente ~30 Hz
```

---

## 🧠 Notas importantes

- ROS 2 usa el **Python del sistema**.
- No se recomienda usar `venv` para nodos ROS.
- Antes de ejecutar el proyecto, asegúrate de cargar:

```bash
source /opt/ros/jazzy/setup.bash
source ~/Documentos/Ros/install/setup.bash
```