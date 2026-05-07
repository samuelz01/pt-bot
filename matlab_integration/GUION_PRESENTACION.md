# Guion de Presentación — Integración MATLAB + ROS 2 + Gazebo
## Robot Seguidor de Línea — Demo de Exposición

---

## Contexto antes de empezar

Tener abierto y visible al mismo tiempo:
- Ventana de **Gazebo** con el robot en la pista (ya ejecutado con `ros2-sim`)
- Ventana de **MATLAB** con los scripts listos
- (Opcional) Una terminal con `ros2-topics` para mostrar los tópicos

---

## Guion hablado

---

### [0:00 – 0:30] Introducción al sistema

> "El proyecto consiste en un robot tricycle simulado en Gazebo Harmonic,
> corriendo dentro de un contenedor Podman con ROS 2 Jazzy sobre Fedora.
>
> Originalmente el robot opera en modo autónomo mediante un nodo de Python
> que procesa imágenes de la cámara con OpenCV. Hoy demostraremos cómo 
> trasladamos toda esa lógica de control y visión hacia MATLAB."

---

### [0:30 – 1:00] Explicar la integración con MATLAB

> "Para integrar MATLAB, no necesitamos instalar ROS en Fedora.
> Aprovechamos que el contenedor de Podman usa la opción `--network host`.
> Esto hace que ROS 2 del contenedor y MATLAB compartan la misma
> interfaz de red.
>
> Usando el estándar DDS con `ROS_DOMAIN_ID = 0`, MATLAB puede descubrir 
> los tópicos de Gazebo de manera transparente, sin bridges intermedios."

---

### [1:00 – 1:30] Demo Oficial Básica (Opcional)

> "Primero validaremos la comunicación pura."

*(Ejecutar `demo_oficial.m` en MATLAB)*

> "Como pueden observar, MATLAB se conectó a ROS 2, recibió el frame
> de la cámara en `/camera/image_raw` y ahora está enviando secuencias de 
> velocidad ciegas a `/cmd_vel` para confirmar que el robot responde."

---

### [1:30 – 2:30] El Plato Fuerte: Demo Line Follower en MATLAB

> "Ahora demostraremos el verdadero potencial: un seguidor de línea
> autónomo programado 100% en MATLAB."

*(Asegurarse de que `demo_oficial` terminó. Ejecutar `demo_line_follower.m`)*

Mientras el robot se mueve, explicar:

> "MATLAB se suscribió a `/camera/image_raw` con una frecuencia de refresco.
> Por cada fotograma, MATLAB extrae la región de interés (la mitad inferior).
>
> Usando algoritmos de visión nativos como `rgb2gray` y `bwareaopen`, 
> binarizamos la imagen para aislar la línea negra. Luego con `regionprops` 
> calculamos el centroide de la línea.
>
> La diferencia entre el centroide y el centro de la cámara nos da el error 
> horizontal. Ese error alimenta un controlador proporcional que determina 
> la velocidad angular (`angular.z`), mientras ajustamos la velocidad lineal 
> en las curvas.
>
> Simultáneamente, estamos calculando un espacio de color HSV para detectar
> la franja roja del final de la pista. Cuando MATLAB identifique una gran 
> concentración de pixeles rojos, mandará velocidad cero y detendrá el robot."

---

### [2:30 – 3:00] Cierre técnico

> "En resumen: hemos logrado separar completamente la planta física
> (que corre en Gazebo dentro de un contenedor Ubuntu) del controlador lógico
> (que corre en MATLAB de forma nativa en Fedora). 
> 
> Esta arquitectura nos permite iterar algoritmos de visión y control 
> utilizando todo el poder de las toolboxes de MATLAB sin alterar el 
> código nativo de la simulación."

---

## Puntos técnicos clave para responder preguntas

| Pregunta probable | Respuesta corta |
|---|---|
| ¿Por qué contenedor? | ROS 2 Jazzy requiere Ubuntu 24.04; Fedora usa Python 3.14 (incompatible) |
| ¿Cómo se comunican? | DDS descubre nodos automáticamente porque el contenedor usa `--network host` |
| ¿Qué es `/cmd_vel`? | Tópico estándar de ROS 2. Envía un `geometry_msgs/Twist` |
| ¿Por qué no corren el de Python y el de MATLAB a la vez? | Ambos pelearían por publicar en `/cmd_vel`, el robot recibiría saltos erráticos |
| ¿Cómo calculan el error en MATLAB? | `regionprops` nos da el centroide de la línea binaria respecto al centro |
