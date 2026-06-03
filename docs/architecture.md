# Arquitectura

## Flujo de co-simulacion

```text
Gazebo -> ROS 2 topics -> MATLAB/Simulink -> ROS 2 /cmd_vel -> carro en Gazebo
```

## Flujo adaptativo futuro

```text
Sensores/Odometria -> estimador adaptativo -> controlador -> /cmd_vel
```

## Responsabilidades

Gazebo:

- Simula `nuevo_mundo.sdf`.
- Carga `models/nuevo_carro/model.sdf`.
- Publica sensores, odometria y estados de juntas.
- Recibe comandos de velocidad por `/cmd_vel`.

ROS 2:

- Expone los topics estables de simulacion.
- Transporta datos entre Gazebo y MATLAB/Simulink.
- Mantiene la configuracion centralizada en `config/topics.yaml`.

MATLAB/Simulink:

- En una fase posterior recibira `/odom`, `/scan`, `/imu` y `/joint_states`.
- Enviara comandos de control a `/cmd_vel`.

Control inteligente/adaptativo:

- No esta implementado todavia.
- La carpeta `robot_control/control/` queda reservada para estimadores,
  controladores y modulos de ajuste de parametros.
