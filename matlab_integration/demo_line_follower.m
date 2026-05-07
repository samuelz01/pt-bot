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

% --- 3. PARAMETROS DEL CONTROLADOR (Afinados para suavidad) ---
vel_lineal_base = 0.20;         % Velocidad maxima (conservadora para evitar zig-zag)
vel_angular_busqueda = 0.5;     % Velocidad de giro cuando pierde la linea (rad/s)
k_p = 0.012;                    % Ganancia Proporcional (reducida para ser mas suave)
k_d = 0.005;                    % Ganancia Derivativa (amortigua las oscilaciones)
zona_muerta = 8;                % Pixeles de tolerancia en el centro donde no gira
alpha_filtro = 0.6;             % Factor de suavizado exponencial (1=sin filtro, menor=mas suave)
area_minima_linea = 300;        % Pixeles minimos para considerar que es la linea
area_minima_meta = 600;         % Pixeles minimos para detectar la meta roja
umbral_negro = 80;              % Intensidad maxima para considerar un pixel como negro (0-255)

% Variables de estado para el control
error_previo = 0;
cx_filtrado = -1;

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
            % Centroide crudo (promedio de posiciones X e Y)
            cx_raw = mean(columnas);
            cy = mean(filas);
            
            % 1. Suavizado Exponencial del centroide (Low-pass filter)
            if cx_filtrado == -1
                cx_filtrado = cx_raw; % Inicializacion
            else
                cx_filtrado = alpha_filtro * cx_raw + (1 - alpha_filtro) * cx_filtrado;
            end
            
            error_pos = cx_filtrado - centro_pantalla;
            
            % 2. Zona Muerta (Dead zone) para evitar micro-oscilaciones en rectas
            if abs(error_pos) < zona_muerta
                error_pos = 0;
            end
            
            % 3. Calculo Derivativo
            error_derivativo = error_pos - error_previo;
            error_previo = error_pos;
            
            % 4. Controlador PD (Proporcional-Derivativo)
            % Frena ligeramente en curvas para no derrapar
            msg_twist.linear.x = max(0.05, vel_lineal_base - abs(error_pos) * 0.002);
            
            % Ecuacion PD: P corrige la posicion, D amortigua la velocidad de acercamiento al centro
            correccion_angular = -(error_pos * k_p + error_derivativo * k_d);
            
            % Saturacion suave (limite maximo de giro a 1.5 rad/s)
            msg_twist.angular.z = max(-1.5, min(1.5, correccion_angular));
            
            % Dibujar centroide suavizado
            plot(ax, cx_filtrado, cy, 'ro', 'MarkerSize', 10, 'LineWidth', 3);
            title(ax, sprintf('Err: %.1f px | Lin: %.2f m/s | Ang: %.2f rad/s', ...
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
