% =========================================================================
% demo_cmdvel.m
% Publica comandos en /cmd_vel de forma basica.
%
% REQUISITOS:
%   1. Contenedor corriendo con --network host
%   2. ros2-sim activo (Gazebo)
%   3. ros2-follower NO DEBE estar corriendo
% =========================================================================

clc; clear; close all;

setenv('ROS_DOMAIN_ID', '0');

disp('=== Creando publicador en /cmd_vel ===');
node = ros2node("/matlab_cmdvel");
pub  = ros2publisher(node, "/cmd_vel", "geometry_msgs/Twist");
pause(1);

msg = ros2message("geometry_msgs/Twist");

disp('Enviando: ADELANTE por 3 segundos...');
msg.linear.x  = 0.3;
msg.angular.z = 0.0;
t_inicio = tic;
while toc(t_inicio) < 3.0
    send(pub, msg);
    pause(0.1);
end

disp('Enviando: GIRAR IZQUIERDA por 2 segundos...');
msg.linear.x  = 0.1;
msg.angular.z = 0.8;
t_inicio = tic;
while toc(t_inicio) < 2.0
    send(pub, msg);
    pause(0.1);
end

disp('Enviando: STOP');
msg.linear.x  = 0.0;
msg.angular.z = 0.0;
send(pub, msg);

disp('=== Secuencia de movimiento finalizada ===');
