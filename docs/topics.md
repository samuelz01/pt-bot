# Topics

## Entradas hacia MATLAB/Simulink

| Topic | Tipo ROS 2 | Uso |
| --- | --- | --- |
| `/odom` | `nav_msgs/msg/Odometry` | Odometria del carro |
| `/scan` | `sensor_msgs/msg/LaserScan` | LiDAR 2D |
| `/imu` | `sensor_msgs/msg/Imu` | IMU del carro |
| `/joint_states` | `sensor_msgs/msg/JointState` | Estados de juntas |
| `/ground_truth_pose` | `geometry_msgs/msg/PoseStamped` | Opcional para experimentos |

## Salida desde MATLAB/Simulink

| Topic | Tipo ROS 2 | Uso |
| --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Comando de velocidad |

## Archivos fuente

- `src/robot_control/config/topics.yaml`
- `src/robot_control/robot_control/interfaces/topic_config.py`
- `src/robot_control/launch/sim_car.launch.py`
