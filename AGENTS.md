# AGENTS.md

## Idioma
Responde siempre en español claro y paso a paso.

## Proyecto
Proyecto de robot con:
- Host Fedora
- MATLAB en el host
- ROS 2 Jazzy + Gazebo dentro de contenedor Podman
- Contenedor con --network host
- ROS_DOMAIN_ID=0
- Ruta host: ~/Documentos/Ros
- Ruta contenedor: /root/Ros

## Estado funcional que NO debe romperse
Actualmente funcionan:
- ros2-sim
- ros2-follower
- MATLAB se conecta a ROS 2
- matlab_integration/demo_line_follower.m controla el robot

No romper esas funciones.

## Reglas estrictas
- No cambiar la arquitectura principal.
- No editar, mover, borrar o renombrar archivos críticos sin revisar referencias antes.
- No romper demo_line_follower.m.
- No romper ros2-sim.
- No romper ros2-follower.
- No cambiar topics ROS como /cmd_vel sin aprobación.
- No ejecutar comandos destructivos como rm, git reset --hard, git clean o git checkout -- sin aprobación.
- Hacer cambios pequeños, seguros y verificables.
- Antes de editar, explicar qué archivos se van a tocar.
- Después de editar, mostrar git status --short y git diff.


## Verificación
Usar estos comandos cuando aplique:

git status --short
git diff
rg "demo_line_follower|ros2-sim|ros2-follower|cmd_vel|ROS_DOMAIN_ID|podman|gazebo|matlab"

## Comandos funcionales conocidos
Host:
cd ~/Documentos/Ros

Contenedor:
cd /root/Ros
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash

Ejecución:
ros2-sim
ros2-follower

MATLAB:
cd('~/Documentos/Ros/matlab_integration')
run('demo_line_follower.m')
