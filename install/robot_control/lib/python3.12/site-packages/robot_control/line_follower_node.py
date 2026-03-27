import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class LineFollowerNode(Node):
    def __init__(self):
        super().__init__('line_follower_node')
        
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # Estado de la carrera
        self.meta_detectada = False
        self.get_logger().info('🏎  Piloto Automático listo. ¡Arrancando!')

    def image_callback(self, msg):
        # Si ya llegamos a la meta, no hacer nada
        if self.meta_detectada:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            height, width, _ = cv_image.shape
            roi = cv_image[height // 2 : height, 0:width]

            # ---- DETECCIÓN DE LA META (color ROJO) ----
            # Gazebo renderiza el rojo como HSV hue ~0 / ~180
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask_rojo1 = cv2.inRange(hsv, np.array([0,  150, 100]), np.array([10, 255, 255]))
            mask_rojo2 = cv2.inRange(hsv, np.array([165,150, 100]), np.array([180,255, 255]))
            mask_meta  = cv2.bitwise_or(mask_rojo1, mask_rojo2)

            area_meta = cv2.countNonZero(mask_meta)

            if area_meta > 600:   # Umbral suficiente para ignorar ruido
                self.meta_detectada = True
                cmd_stop = Twist()  # todo en 0 → frena
                self.publisher_.publish(cmd_stop)
                self.get_logger().info('🏁 ¡META DETECTADA! Robot detenido.')
                cv2.imshow("Vista de Suelo (ROI)", roi)
                cv2.waitKey(1)
                return

            # ---- DETECCIÓN DE LA LÍNEA NEGRA (Otsu + fijo) ----
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, mask_otsu  = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            _, mask_fixed = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
            mask = cv2.bitwise_or(mask_otsu, mask_fixed)

            # Quitar ruido
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            m   = cv2.moments(mask)
            cmd = Twist()

            if m['m00'] > 500:
                cx     = int(m['m10'] / m['m00'])
                cy     = int(m['m01'] / m['m00'])
                centro = width // 2
                error  = cx - centro

                # Controlador P: desacelera en curvas
                cmd.linear.x  = max(0.05, 0.25 - abs(error) * 0.003)
                cmd.angular.z = max(-1.8, min(1.8, -float(error) * 0.018))

                if   cx < (centro - 40): self.get_logger().info(f'IZQUIERDA | cx={cx}')
                elif cx > (centro + 40): self.get_logger().info(f'DERECHA   | cx={cx}')
                else:                    self.get_logger().info(f'CENTRO    | cx={cx}')

                cv2.circle(roi, (cx, cy), 10, (0, 255, 0), -1)
                cv2.line(roi, (centro, 0), (centro, roi.shape[0]), (255, 0, 0), 1)
            else:
                # Línea perdida → gira buscando (curva siempre es a la izquierda)
                self.get_logger().info('¡Línea perdida! Buscando...')
                cmd.linear.x  = 0.0
                cmd.angular.z = 0.6

            self.publisher_.publish(cmd)
            cv2.imshow("Vista de Suelo (ROI)", roi)
            cv2.imshow("Mascara Binaria",      mask)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = LineFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
