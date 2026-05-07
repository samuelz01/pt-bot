% =========================================================================
% conectar_ros2.m
% Verifica la conexión MATLAB <-> ROS 2 del contenedor.
%
% ANTES de ejecutar:
%   1. El contenedor ros2_jazzy debe estar corriendo con --network host
%   2. La simulación debe estar activa (ros2-sim)
% =========================================================================

clc; clear; close all;

disp('=== Conectando a ROS 2 ===');

% Forzar ROS_DOMAIN_ID = 0 (compartido con el contenedor)
setenv('ROS_DOMAIN_ID', '0');

% Crear nodo MATLAB en la red ROS 2
node = ros2node("/matlab_conector");
pause(1);  % Dar tiempo a que el nodo se anuncie

disp('Nodo MATLAB creado: /matlab_conector');

%% -- Listar tópicos disponibles --
disp(' ');
disp('=== Topicos disponibles en la red ROS 2 ===');
topics = ros2("topic", "list");
disp(topics);

%% -- Verificar tópicos clave del proyecto --
disp('=== Verificando topicos del proyecto ===');

topicos_esperados = {"/cmd_vel", "/camera/image_raw"};
for i = 1:length(topicos_esperados)
    t = topicos_esperados{i};
    if any(strcmp(topics, t))
        fprintf('  [OK]  %s encontrado\n', t);
    else
        fprintf('  [--]  %s NO encontrado (¿esta corriendo ros2-sim?)\n', t);
    end
end

disp(' ');
disp('=== Conexion verificada ===');
