# AGENTS.md

## Idioma

Responde siempre en español claro y paso a paso.

## Proyecto y Contexto Colaborativo

Este es un proyecto de robótica híbrido y **colaborativo desarrollado por dos personas**:
1. **Desarrollador 1 (Ubuntu Nativo):** Trabaja directamente en su host usando ROS 2 Jazzy. Todo lo relacionado a contenedores debe ser ignorado por él.
2. **Desarrollador 2 (Fedora Contenedor):** Depende de la carpeta `container/` usando Podman con `--network host` y `ROS_DOMAIN_ID=0` para aislar el entorno.

Ambos comparten este repositorio. Las respuestas y acciones de la IA deben respetar siempre a ambos desarrolladores y no romper el flujo de trabajo de ninguno de los dos.

## Arquitectura actual

El proyecto incluye co-simulación de un robot mecanum con MATLAB/Simulink.

- Mundo principal: `src/robot_control/worlds/nuevo_mundo.sdf`.
- Mundo vacío (Con Fricciones): `src/robot_control/launch/sim_empty_world_fricciones.launch.py`.
- Mundo vacío (Sin Fricciones / Uniforme): `src/robot_control/launch/sim_empty_world_uniform.launch.py`.
- Carro principal: `src/robot_control/models/nuevo_carro/model.sdf`.
- Launch principal: `src/robot_control/launch/sim_car.launch.py`.
- Interfaces base para MATLAB/Simulink en `robot_control/interfaces/`.

Flujo de lazo cerrado preparado:
```text
Gazebo -> ROS 2 topics -> MATLAB/Simulink -> ROS 2 /cmd_vel -> carro en Gazebo
```

Flujo adaptativo futuro:
```text
Sensores/Odometria -> estimador adaptativo -> controlador -> /cmd_vel
```

## Reglas

- Al sugerir comandos de terminal, **diferencia claramente** entre el entorno nativo en Ubuntu y el entorno en contenedor para Fedora.
- Nunca recomiendes eliminar la carpeta `container/` ni sus scripts.
- No cambiar el topic base `/cmd_vel` sin aprobación expresa.
- Mantener `ros2-sim` como comando principal de simulación para el usuario de Fedora.
- Hacer cambios pequeños, verificables y acordes con la arquitectura modular.
- Antes de editar, explicar qué archivos se van a tocar.

## Comandos Funcionales (Nativo - Ubuntu)

Compilación:
```zsh
source /opt/ros/jazzy/setup.zsh
colcon build --symlink-install
```

Ejecución principal:
```zsh
source install/setup.zsh
export QT_QPA_PLATFORM=xcb
ros2 launch robot_control sim_car.launch.py
ros2 run robot_control simulink_router
```

Opciones extra:
```zsh
ros2 launch robot_control sim_empty_world_fricciones.launch.py
ros2 launch robot_control sim_empty_world_uniform.launch.py
ros2 run robot_control keyboard_teleop
```

## Comandos Funcionales (Contenedor - Fedora)

Host:
```bash
bash container/rebuild.sh
ros2-sim
```

Contenedor:
```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch robot_control sim_car.launch.py
```
