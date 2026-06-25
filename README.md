# Proyecto ROS 2 Jazzy + Gazebo + MATLAB/Simulink

Este repositorio es el espacio de trabajo colaborativo para dos desarrolladores que utilizan sistemas operativos distintos:
- **Usuario de Ubuntu:** Ejecuta ROS 2 Jazzy y Gazebo de forma nativa.
- **Usuario de Fedora:** Ejecuta el entorno a través de un contenedor Podman aislado.

El proyecto proporciona una base limpia, modular y escalable para la simulación y co-simulación de un **robot con tracción Mecanum** en Gazebo, integrando algoritmos de control desde MATLAB/Simulink.

---

## Descripción Técnica del Proyecto

Este proyecto está construido sobre las siguientes tecnologías y conceptos:

### 1. El Robot (Mecanum Bot)
El robot simulado (`src/robot_control/models/nuevo_carro/model.sdf`) es un vehículo tipo "skid-steer" o tracción Mecanum. Este tipo de ruedas le permiten ser un **robot holonómico**, es decir, capaz de moverse en cualquier dirección instantáneamente (adelante, atrás, rotación e incluso traslación lateral pura).

**Sensores equipados:**
- **Odometría (IMU/Encoders simulados):** Estima la posición espacial (X, Y, Z) y la orientación (Cuaterniones) del robot, además de sus velocidades lineales y angulares.
- **LiDAR 2D:** Escáner láser que emite rayos en 360 grados para detectar la distancia exacta a los obstáculos alrededor del robot.
- **Cámara:** Sensor visual frontal que captura el entorno en formato de imagen, útil para tareas futuras de visión computacional.

### 2. Arquitectura de Software
- **ROS 2 Jazzy:** Es el *middleware* de comunicación. Define cómo viajan los datos (a través de topics) y organiza el código en paquetes.
- **Gazebo:** Es el motor de físicas. Calcula las colisiones, la gravedad, la fricción de las llantas y genera los datos de los sensores.
- **ros_gz_bridge:** Un puente esencial incluido en los *launch files* que toma los datos internos de Gazebo y los convierte en mensajes estándar de ROS 2 (`sensor_msgs`, `nav_msgs`, etc.).

### 3. El Nodo Enrutador (`simulink_router_node.py`)
Es la pieza clave para la co-simulación. En lugar de que Simulink hable directamente con Gazebo (lo cual puede generar conflictos o mensajes perdidos), este nodo escrito en Python hace de "semáforo y filtro":
1. **Recopila** todos los datos de los sensores de ROS 2.
2. **Imprime** un resumen en la terminal a 1 Hz (Posición actual, distancia mínima del LiDAR y estado de la cámara) para que el desarrollador sepa que la simulación está viva.
3. **Crea un canal exclusivo** para Simulink: Redirige la odometría hacia `/simulink/odom_filtered` y escucha comandos de movimiento en `/simulink/cmd_vel`, pasándolos finalmente a Gazebo (`/cmd_vel`).

---

## Opciones de Instalación y Ejecución (Entorno Híbrido)

Dependiendo de tu sistema operativo, elige la opción correspondiente:

### Opción A: Instalación Nativa (Ubuntu)

**1. Compilación:**
```zsh
source /opt/ros/jazzy/setup.zsh
colcon build --symlink-install
```

**2. Ejecución Base:**
Abre dos terminales para correr la simulación y el enrutador:

*Terminal 1 (Gazebo con el mundo principal):*
```zsh
source /opt/ros/jazzy/setup.zsh
source install/setup.zsh
export QT_QPA_PLATFORM=xcb
ros2 launch robot_control sim_car.launch.py
```

*Terminal 2 (Router para Simulink):*
```zsh
source /opt/ros/jazzy/setup.zsh
source install/setup.zsh
ros2 run robot_control simulink_router
```

### Opción B: Instalación por Contenedor (Fedora / Otros)

Si utilizas Fedora, no alteres tu sistema e inicia el contenedor Podman incluido.

**1. Construcción de Imagen (Solo primera vez o al hacer cambios base):**
```bash
bash container/rebuild.sh
```

**2. Ejecución del Entorno:**
Levanta el contenedor con el siguiente alias/script:
```bash
ros2-sim
```

*(Dentro del contenedor)*
```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch robot_control sim_car.launch.py
```

---

## Diferentes Opciones de Ejecución y Herramientas

Además de la ejecución base, el paquete incluye opciones para pruebas y depuración:

### 1. Teleoperación por Teclado
Si deseas mover el carro manualmente para probar la física de Gazebo sin depender de Simulink, ejecuta el nodo de teleoperación en una terminal extra.

**Nativo en Ubuntu (Zsh):**
```zsh
source install/setup.zsh
ros2 run robot_control keyboard_teleop
```

**Contenedor en Fedora (Bash):**
```bash
source install/setup.bash
ros2 run robot_control keyboard_teleop
```
*Usa las teclas W, A, S, D para mover el robot.*

### 2. Simuladores con Mundo Vacío
Si quieres probar algoritmos matemáticos sin el ruido de obstáculos (por ejemplo, calibración pura de odometría), lanza alguno de los mundos vacíos en lugar del principal.

**Nativo en Ubuntu (Zsh):**
```zsh
source install/setup.zsh
ros2 launch robot_control sim_empty_world_fricciones.launch.py  # Mundo con fricciones variadas
# Opcionalmente:
# ros2 launch robot_control sim_empty_world_uniform.launch.py   # Mundo uniforme
```

**Contenedor en Fedora (Bash):**
```bash
source install/setup.bash
ros2 launch robot_control sim_empty_world_fricciones.launch.py  # Mundo con fricciones variadas
# Opcionalmente:
# ros2 launch robot_control sim_empty_world_uniform.launch.py   # Mundo uniforme
```

---

## Ejemplos de MATLAB/Simulink

Dentro de la carpeta `matlab_integration/simulink/` se encuentran 3 modelos listos para probar la comunicación. Para usarlos, asegúrate de tener la simulación en Gazebo y el nodo `simulink_router` corriendo.

1. **`ejemplo_1_enviar_velocidad.slx`**: 
   - **Objetivo**: Pruebas de lazo abierto.
   - **Descripción**: Envía comandos de velocidad fijos (lineal y angular) desde Simulink hacia el topic `/simulink/cmd_vel`. Sirve para confirmar que MATLAB tiene permisos para escribir en la red de ROS 2 y mover el carro.
   
2. **`ejemplo_2_leer_odometria.slx`**:
   - **Objetivo**: Monitoreo de sensores.
   - **Descripción**: Se suscribe al topic `/simulink/odom_filtered`. Utiliza bloques de deserialización para separar el mensaje de ROS 2 y extraer la posición (X, Y) y la orientación, graficándola en un "Scope" (osciloscopio) en tiempo real.

### Análisis Profundo: `ejemplo_3_lazo_cerrado_router.slx`

Este es el ejemplo más importante del proyecto, ya que demuestra la **verdadera co-simulación en Lazo Cerrado (Closed-Loop Control)**. Así es como funciona paso a paso:

1. **Lectura de la Realidad (Feedback):** 
   El modelo inicia leyendo el topic `/simulink/odom_filtered`. Extrae la posición actual del robot en el plano cartesiano (X_actual, Y_actual) y su orientación (Yaw o ángulo hacia dónde mira el frente del robot).
   
2. **Cálculo del Error:**
   Dentro de Simulink, hay un punto objetivo definido (SetPoint), por ejemplo, llegar a la coordenada `(X=5, Y=5)`. Simulink resta la posición actual menos el SetPoint para calcular el **Error de Posición**. También calcula el **Error de Ángulo** (cuánto tiene que girar el robot para mirar hacia su objetivo).

3. **El Controlador (PD / Proporcional-Derivativo):**
   Los errores calculados ingresan a un sistema de control matemático. 
   - La parte **Proporcional (P)** acelera el robot si está muy lejos y lo frena suavemente conforme se acerca al objetivo.
   - La parte **Derivativa (D)** evita movimientos bruscos y oscilaciones, estabilizando el giro (por ejemplo, para dar curvas precisas de 90 grados sin derrapar o pasarse de largo debido a la inercia del peso del robot en Gazebo).

4. **Acción (Output):**
   El controlador escupe dos números: Velocidad Lineal (para avanzar) y Velocidad Angular (para girar). Simulink empaqueta estos dos números en un mensaje de ROS 2 (`geometry_msgs/Twist`) y lo envía a través de la red al topic `/simulink/cmd_vel`.

5. **El Ciclo se Repite:**
   El `simulink_router` toma este comando, Gazebo mueve el robot, la posición cambia, y el ciclo vuelve a empezar instantáneamente. Todo esto ocurre decenas de veces por segundo hasta que el Error de Posición es cero, momento en el cual Simulink ordena velocidad 0 y el robot se detiene exactamente en el punto deseado.
