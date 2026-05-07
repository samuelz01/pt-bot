% =========================================================================
% demo_line_follower.m
% Seguidor de linea autonomo implementado puramente en MATLAB base.
% (No requiere Image Processing Toolbox)
%
% REQUISITOS OBLIGATORIOS:
%   - ros2-sim corriendo en la terminal
%   - ros2-follower APAGADO (no pueden correr al mismo tiempo)
% =========================================================================

clc; clear; close all;

setenv('ROS_DOMAIN_ID', '0');
disp('====================================================');
disp('SEGUIDOR DE LINEA AUTONOMO DESDE MATLAB');
disp('====================================================');

% --- 1. CONEXION A ROS 2 ---
node = ros2node("/matlab_line_follower");
pub  = ros2publisher(node, "/cmd_vel", "geometry_msgs/Twist");
sub  = ros2subscriber(node, "/camera/image_raw", "sensor_msgs/Image");

msg_twist = ros2message("geometry_msgs/Twist");

disp('Esperando conexion con la camara (max 10s)...');
primer_msg = false;
t_wait = tic;
while toc(t_wait) < 10
    if ~isempty(sub.LatestMessage)
        primer_msg = true;
        break;
    end
    pause(0.5);
end

if ~primer_msg
    error('No se recibio ninguna imagen. Verifica que ros2-sim esta activo.');
end
disp('Conexion establecida. Iniciando control...');

% --- 2. CONFIGURACION DE VISUALIZACION ---
fig = figure('Name', 'Vision - MATLAB Line Follower', 'NumberTitle', 'off');
ax = axes(fig);
disp('Presiona Ctrl+C o cierra la ventana de la figura para detener.');

% --- 3. PARAMETROS DEL CONTROLADOR ---
vel_lineal_base = 0.25;         % Velocidad maxima hacia adelante (m/s)
vel_angular_busqueda = 0.6;     % Velocidad de giro cuando pierde la linea (rad/s)
k_p = 0.018;                    % Ganancia proporcional para el giro
area_minima_linea = 300;        % Pixeles minimos para considerar que es la linea
area_minima_meta = 600;         % Pixeles minimos para detectar la meta roja
umbral_negro = 80;              % Intensidad maxima para considerar un pixel como negro (0-255)

% --- 4. BUCLE PRINCIPAL ---
while ishandle(fig)
    try
        % Leer ultimo frame sin bloquear
        msg_img = sub.LatestMessage;
        if isempty(msg_img)
            pause(0.05); continue;
        end
        
        img = rosReadImage(msg_img);
        [alto, ancho, ~] = size(img);
        
        % ROI: Mitad inferior de la imagen (solo vemos el suelo frente al robot)
        region = img(floor(alto/2):end, :, :);
        
        % --- DETECCION DE META ROJA (HSV es nativo en MATLAB base) ---
        hsv = rgb2hsv(region);
        mask_roja = (hsv(:,:,1) < 0.05 | hsv(:,:,1) > 0.95) & (hsv(:,:,2) > 0.5) & (hsv(:,:,3) > 0.4);
        
        if sum(mask_roja(:)) > area_minima_meta
            disp('!META DETECTADA! Frenando el robot.');
            msg_twist.linear.x = 0;
            msg_twist.angular.z = 0;
            send(pub, msg_twist);
            
            imshow(region, 'Parent', ax);
            title(ax, 'META ROJA DETECTADA - STOP', 'Color', 'r', 'FontWeight', 'bold');
            break; % Salir del bucle
        end
        
        % --- DETECCION DE LINEA NEGRA (Sin toolboxes) ---
        % Convertir a escala de grises manualmente para no depender de rgb2gray
        region_double = double(region);
        gris = 0.2989 * region_double(:,:,1) + 0.5870 * region_double(:,:,2) + 0.1140 * region_double(:,:,3);
        
        % Umbral fijo simple
        mask_negra = gris < umbral_negro;
        
        % --- CALCULO DE ERROR Y CONTROL ---
        % Encontrar coordenadas de todos los pixeles negros
        [filas, columnas] = find(mask_negra);
        area_linea = length(columnas);
        
        % Dibujar imagen original como fondo
        imshow(region, 'Parent', ax); hold(ax, 'on');
        centro_pantalla = ancho / 2;
        
        % Dibujar linea del centro de la pantalla
        plot(ax, [centro_pantalla centro_pantalla], [1 size(region,1)], 'b--', 'LineWidth', 2);
        
        if area_linea > area_minima_linea
            % Centroide calculado manualmente (promedio de posiciones X e Y)
            cx = mean(columnas);
            cy = mean(filas);
            
            error_pos = cx - centro_pantalla;
            
            % Control Proporcional
            % Frena un poco linealmente en las curvas muy cerradas
            msg_twist.linear.x = max(0.05, vel_lineal_base - abs(error_pos) * 0.003);
            % Gira en proporcion al error
            msg_twist.angular.z = max(-1.8, min(1.8, -error_pos * k_p));
            
            % Dibujar centroide de la linea
            plot(ax, cx, cy, 'r+', 'MarkerSize', 12, 'LineWidth', 3);
            title(ax, sprintf('Error: %.1f px | Lineal: %.2f m/s | Angular: %.2f rad/s', ...
                              error_pos, msg_twist.linear.x, msg_twist.angular.z));
        else
            % Linea muy pequeña o no hay -> Buscar
            msg_twist.linear.x = 0.0;
            msg_twist.angular.z = vel_angular_busqueda;
            title(ax, 'Linea perdida o muy pequeña. Buscando...');
        end
        
        hold(ax, 'off');
        drawnow limitrate;
        
        % Enviar el comando al robot
        send(pub, msg_twist);
        
        % Pequeña pausa para sincronizar a ~30 fps sin saturar CPU
        pause(0.03);
        
    catch ME
        % Mostrar error de MATLAB si algo falla repentinamente
        disp(['[ERROR]: ' ME.message]);
        pause(1);
    end
end

% Paro de seguridad al cerrar la ventana
disp('Deteniendo robot...');
msg_twist.linear.x = 0;
msg_twist.angular.z = 0;
send(pub, msg_twist);
disp('Fin del control.');
