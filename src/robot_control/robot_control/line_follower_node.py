import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np


class NodoSeguidor(Node):
    """Nodo ROS 2 que sigue una línea negra usando visión por cámara."""

    def __init__(self):
        super().__init__('line_follower_node')  # ← nombre del nodo en ROS 

        # Suscriptor a las imágenes de la cámara
        self.suscripcion = self.create_subscription(
            Image, '/camera/image_raw', self.procesar_imagen, 10)

        # Publicador de comandos de velocidad hacia el robot
        self.publicador = self.create_publisher(Twist, '/cmd_vel', 10)

        # Puente de conversión entre mensajes ROS y matrices OpenCV
        self.puente_cv = CvBridge()

        # Bandera que indica si el robot detectó la meta y debe frenar
        self.meta_detectada = False

        # Crear las ventanas de diagnóstico UNA SOLA VEZ aquí.
        # cv2.imshow() con un nombre ya existente 
        # ACTUALIZA la ventana, no crea una nueva.
        # Sin esta inicialización, cada llamada a imshow() abriría una ventana distinta.
        cv2.namedWindow("Vista de Suelo",  cv2.WINDOW_NORMAL)
        cv2.namedWindow("Máscara Binaria", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Vista de Suelo",  320, 120)
        cv2.resizeWindow("Máscara Binaria", 320, 120)

        self.get_logger().info('🏎  Piloto Automático listo. ¡Arrancando!')

    def procesar_imagen(self, mensaje):
        """Callback que se ejecuta en cada fotograma recibido de la cámara."""

        # Si ya llegamos a la meta, ignorar todos los fotogramas siguientes
        if self.meta_detectada:
            return

        try:
            # Convertir el mensaje ROS a una imagen BGR de OpenCV
            imagen = self.puente_cv.imgmsg_to_cv2(mensaje, "bgr8")
            alto, ancho, _ = imagen.shape

            # Región de interés: mitad inferior de la imagen (el suelo próximo)
            region = imagen[alto // 2 : alto, 0:ancho]

            # ── DETECCIÓN DE LA META (franja roja) ───────────────────────
            # Convertimos a HSV para filtrar por matiz de color
            espacio_hsv  = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
            mascara_roja1 = cv2.inRange(espacio_hsv,
                                        np.array([0,   150, 100]),
                                        np.array([10,  255, 255]))
            mascara_roja2 = cv2.inRange(espacio_hsv,
                                        np.array([165, 150, 100]),
                                        np.array([180, 255, 255]))
            mascara_meta = cv2.bitwise_or(mascara_roja1, mascara_roja2)
            area_roja    = cv2.countNonZero(mascara_meta)

            if area_roja > 600:
                self.meta_detectada = True
                self.publicador.publish(Twist())  # Twist vacío = freno total
                self.get_logger().info('🏁 ¡META DETECTADA! Robot detenido.')
                cv2.imshow("Vista de Suelo", region)
                cv2.waitKey(1)
                return

            # ── DETECCIÓN DE LA LÍNEA NEGRA ──────────────────────────────
            escala_grises  = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

            # Umbral Otsu: calcula el corte óptimo automáticamente según el histograma
            _, mascara_otsu = cv2.threshold(
                escala_grises, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Umbral fijo de respaldo para ampliar la detección en zonas de sombra
            _, mascara_fija = cv2.threshold(escala_grises, 100, 255, cv2.THRESH_BINARY_INV)

            # Combinar ambas máscaras y eliminar ruido pequeño
            mascara = cv2.bitwise_or(mascara_otsu, mascara_fija)
            nucleo  = np.ones((5, 5), np.uint8)
            mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, nucleo)

            # ── CONTROLADOR PROPORCIONAL (P) ─────────────────────────────
            momentos = cv2.moments(mascara)
            comando  = Twist()

            if momentos['m00'] > 500:
                # Centro geométrico de la mancha blanca (la línea)
                centro_x = int(momentos['m10'] / momentos['m00'])
                centro_y = int(momentos['m01'] / momentos['m00'])
                centro_pantalla = ancho // 2
                error = centro_x - centro_pantalla  # + = derecha, - = izquierda

                # Velocidad lineal: se reduce conforme mayor sea el error de giro
                comando.linear.x  = max(0.05, 0.25 - abs(error) * 0.003)
                # Velocidad angular proporcional al error (corrección suave)
                comando.angular.z = max(-1.8, min(1.8, -float(error) * 0.018))

                # Registro de diagnóstico en consola
                if   centro_x < (centro_pantalla - 40):
                    self.get_logger().info(f'IZQUIERDA | cx={centro_x}')
                elif centro_x > (centro_pantalla + 40):
                    self.get_logger().info(f'DERECHA   | cx={centro_x}')
                else:
                    self.get_logger().info(f'CENTRO    | cx={centro_x}')

                # Dibujar marcadores de diagnóstico en la vista
                cv2.circle(region, (centro_x, centro_y), 10, (0, 255, 0), -1)
                cv2.line(region,
                         (centro_pantalla, 0),
                         (centro_pantalla, region.shape[0]),
                         (255, 0, 0), 1)
            else:
                # Línea fuera del campo visual → girar buscando (curva siempre a la izq.)
                self.get_logger().info('¡Línea perdida! Girando en búsqueda...')
                comando.linear.x  = 0.0
                comando.angular.z = 0.6

            self.publicador.publish(comando)

            # Actualizar las ventanas (no crea nuevas, solo refresca las del __init__)
            cv2.imshow("Vista de Suelo",  region)
            cv2.imshow("Máscara Binaria", mascara)
            cv2.waitKey(1)

        except Exception as excepcion:
            self.get_logger().error(f'Error al procesar imagen: {excepcion}')


def main(args=None):
    rclpy.init(args=args)
    nodo = NodoSeguidor()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        nodo.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
