% =========================================================================
% monitor_cmdvel.m
% Monitorea y grafica lo que se publica en /cmd_vel en tiempo real.
% =========================================================================

clc; clear; close all;

setenv('ROS_DOMAIN_ID', '0');
disp('=== Monitor en tiempo real de /cmd_vel ===');
node = ros2node("/matlab_monitor");

fig = figure('Name', 'Monitor /cmd_vel', 'NumberTitle', 'off');
tiledlayout(2,1);

nexttile;
h1 = animatedline('Color', 'b', 'LineWidth', 2);
ylabel('linear.x (m/s)'); grid on; title('Velocidad Lineal');

nexttile;
h2 = animatedline('Color', 'r', 'LineWidth', 2);
ylabel('angular.z (rad/s)'); xlabel('Tiempo (s)'); grid on; title('Velocidad Angular');

global g_msg_nuevo g_lx g_az;
g_msg_nuevo = false; g_lx = 0; g_az = 0;

sub = ros2subscriber(node, "/cmd_vel", "geometry_msgs/Twist", @cbCmdVel);

disp('Monitoreando... Cierra la ventana para salir.');
t0 = tic;

while ishandle(fig)
    pause(0.05);
    if g_msg_nuevo
        t = toc(t0);
        addpoints(h1, t, g_lx);
        addpoints(h2, t, g_az);
        drawnow limitrate;
        g_msg_nuevo = false;
    end
end
disp('=== Monitor finalizado ===');

function cbCmdVel(msg)
    global g_msg_nuevo g_lx g_az;
    g_lx = msg.linear.x;
    g_az = msg.angular.z;
    g_msg_nuevo = true;
end
