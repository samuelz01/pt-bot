% =========================================================================
% demo_camara.m
% Recibe y muestra la imagen del robot desde Gazebo.
% =========================================================================

clc; clear; close all;

setenv('ROS_DOMAIN_ID', '0');
disp('=== Conectando a /camera/image_raw ===');
node = ros2node("/matlab_camara");
sub_cam = ros2subscriber(node, "/camera/image_raw", "sensor_msgs/Image");

disp('Esperando imagen... (max 5 seg)');
try
    msg = receive(sub_cam, 5);
    img = rosReadImage(msg);
    figure('Name', 'Camara del Robot', 'NumberTitle', 'off');
    imshow(img);
    title(sprintf('Resolucion: %d x %d', msg.width, msg.height));
    disp('Imagen recibida y mostrada.');
catch
    disp('Error: No se recibio la imagen. ¿Esta activo ros2-sim?');
end
