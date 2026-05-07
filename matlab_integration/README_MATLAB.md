# Integración MATLAB ↔ ROS 2 Jazzy — Robot Seguidor de Línea

> **Aclaración importante:** No se modificó la lógica principal del proyecto.
> Solo se añadieron los scripts MATLAB de esta carpeta como capa externa de integración.

---

## Arquitectura de la integración

```
┌─────────────────────────────────────────────────────────────────────┐
│  HOST FEDORA                                                        │
│                                                                     │
│   MATLAB (nativo en host)                                          │
│     ├── publica → /cmd_vel  (geometry_msgs/Twist)  ← OBLIGATORIO  │
│     └── recibe  ← /camera/image_raw (sensor_msgs/Image) ← OPCIONAL │
│                          │                                          │
│                   DDS UDP sobre loopback                            │
│                   (posible por --network host)                      │
│                          │                                          │
│  ┌───────────────────────┴──────────────────────────────────────┐  │
│  │  Contenedor Podman: ros2_jazzy  (Ubuntu 24.04)               │  │
│  │  Arrancado con --network host  ← REQUISITO OBLIGATORIO       │  │
│  │                                                              │  │
│  │  Gazebo Harmonic                                             │  │
│  │    └─ Tricycle Bot  (plugin DiffDrive)                       │  │
│  │         ├─ escucha /cmd_vel → mueve el robot                 │  │
│  │         └─ publica camera/image_raw (30 FPS)                 │  │
│  │                  ↕                                           │  │
│  │  ros_gz_bridge  (parameter_bridge)                           │  │
│  │    /cmd_vel           geometry_msgs/Twist ↔ gz.msgs.Twist    │  │
│  │    /camera/image_raw  sensor_msgs/Image   ↔ gz.msgs.Image    │  │
│  │                                                              │  │
│  │  line_follower_node  ← NO CORRER durante la demo MATLAB      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

ROS_DOMAIN_ID = 0  (compartido por host y contenedor via --network host)
```

---

## ⚠️ Restricción crítica: `ros2-follower` y MATLAB son mutuamente excluyentes

Ambos publican en `/cmd_vel`. Si los dos corren al mismo tiempo, el robot
recibirá comandos contradictorios y su comportamiento será impredecible.

| Modo | Qué corre en terminal | Qué corre en MATLAB |
|---|---|---|
| Autónomo (Python) | `ros2-follower` | Ningún controlador |
| Oficial (Respald) | Ninguno | `demo_oficial.m` |
| MATLAB Follower | Ninguno | `demo_line_follower.m` |

---

## Requisitos previos — OBLIGATORIOS

1. **Contenedor corriendo con `--network host`**.
2. **`ROS_DOMAIN_ID = 0`** en MATLAB (es el valor por defecto; no hace falta configurarlo).
3. **`ros2-sim` activo** antes de ejecutar cualquier script MATLAB.

---

## Scripts MATLAB — descripción

| Archivo | Propósito |
|---|---|
| `conectar_ros2.m` | Conecta a ROS 2 y lista los tópicos disponibles para validación |
| `monitor_cmdvel.m` | Monitorea `/cmd_vel` con gráfica animada en tiempo real |
| `demo_cmdvel.m` | Prueba rápida de publicación de velocidades en `/cmd_vel` |
| `demo_camara.m` | Captura y muestra un fotograma de `/camera/image_raw` |
| **`demo_oficial.m`** | **Demo oficial de integración básica** (mueve el robot con secuencias fijas) |
| **`demo_line_follower.m`** | **Demo de Seguidor de Línea 100% MATLAB** (recibe cámara, binariza y controla el robot en tiempo real) |

---

## Secuencia Recomendada para la Exposición

### 1. Arranque del entorno (Terminal)
```bash
# Iniciar simulación (siempre primero)
ros2-sim
```

### 2. Demo Autónoma Original (Prueba de vida)
```bash
# En otra terminal
ros2-follower
```
*(Dejar que el robot recorra un poco la pista y luego detener con Ctrl+C)*

### 3. Demo MATLAB Oficial (Respaldo)
Desde MATLAB, ejecutar `demo_oficial.m`.  
Esto demostrará que MATLAB puede comunicarse exitosamente por DDS con el contenedor y mover el robot usando comandos de velocidad estáticos y obtener la cámara.

### 4. Demo MATLAB Line Follower (El plato fuerte)
Asegúrate de que `ros2-follower` y `demo_oficial.m` estén detenidos.  
Desde MATLAB, ejecuta `demo_line_follower.m`.  
MATLAB recibirá el streaming de la cámara, aislará la línea negra con procesamiento de imágenes (regionprops), aplicará control proporcional al error y conducirá al robot hasta la meta roja.
