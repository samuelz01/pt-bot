# AGENTS.md

## Idioma

Responde siempre en espanol claro y paso a paso.

## Proyecto

Proyecto de robot con:

- Host Fedora.
- MATLAB/Simulink previsto en el host.
- ROS 2 Jazzy + Gazebo dentro de contenedor Podman.
- Contenedor con `--network host`.
- `ROS_DOMAIN_ID=0`.
- Ruta host: `~/Documentos/Ros`.
- Ruta contenedor: `/root/Ros`.

## Arquitectura actual

El repositorio conserva solo la nueva base:

- Mundo principal: `src/robot_control/worlds/nuevo_mundo.sdf`.
- Carro principal: `src/robot_control/models/nuevo_carro/model.sdf`.
- Launch principal: `src/robot_control/launch/sim_car.launch.py`.
- Interfaces base para MATLAB/Simulink en `robot_control/interfaces/`.

Flujo preparado:

```text
Gazebo -> ROS 2 topics -> MATLAB/Simulink -> ROS 2 /cmd_vel -> carro en Gazebo
```

Flujo adaptativo futuro:

```text
Sensores/Odometria -> estimador adaptativo -> controlador -> /cmd_vel
```

## Reglas

- No cambiar `/cmd_vel` sin aprobacion.
- Mantener `ros2-sim` como comando principal de simulacion.
- No implementar Simulink completo ni red neuronal hasta pedirlo explicitamente.
- Hacer cambios pequenos, verificables y acordes con la arquitectura modular.
- Antes de editar, explicar que archivos se van a tocar.
- Despues de editar, mostrar `git status --short` y `git diff`.

## Verificacion

Usar cuando aplique:

```bash
git status --short
git diff
rg "sim_car|nuevo_mundo|nuevo_carro|cmd_vel|ROS_DOMAIN_ID|podman|gazebo|matlab|simulink"
```

## Comandos funcionales

Host:

```bash
cd ~/Documentos/Ros
bash container/rebuild.sh
ros2-sim
```

Contenedor:

```bash
cd /root/Ros
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch robot_control sim_car.launch.py
```
