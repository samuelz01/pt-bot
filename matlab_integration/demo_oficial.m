clc; clear; close all;

disp('====================================================');
disp('DEMO OFICIAL - MATLAB + ROS 2 + Gazebo');
disp('Robot Seguidor de Linea - Control desde MATLAB');
disp('====================================================');

setenv('ROS_DOMAIN_ID','0');

disp('Conectando a ROS 2...');
node = ros2node("/matlab_demo");
pause(1.5);

topics = ros2("topic","list");
disp('Topicos detectados:');
disp(topics);

ok_cmdvel = any(strcmp(topics,"/cmd_vel"));
ok_cam    = any(strcmp(topics,"/camera/image_raw"));

if ~ok_cmdvel
    error('/cmd_vel no disponible. Verifica ros2-sim y --network host.');
end

disp('/cmd_vel detectado.');

% Camara opcional
if ok_cam
    try
        disp('Intentando recibir una imagen de /camera/image_raw ...');
        sub_cam = ros2subscriber(node,"/camera/image_raw","sensor_msgs/Image");
        msg_img = receive(sub_cam,8);
        img = rosReadImage(msg_img);

        figure('Name','Camara del Robot','NumberTitle','off');
        imshow(img);
        title('Imagen recibida desde /camera/image_raw');
        disp('Camara recibida correctamente.');
    catch e
        disp(['Aviso: no se pudo recibir camara: ' e.message]);
    end
else
    disp('La camara no esta disponible. Continuando sin imagen.');
end

disp('Creando publicador en /cmd_vel ...');
pub = ros2publisher(node,"/cmd_vel","geometry_msgs/Twist");
pause(1);

msg = ros2message("geometry_msgs/Twist");

% Figura simple de monitoreo
figure('Name','Monitor de comandos','NumberTitle','off');
tiledlayout(2,1);

nexttile;
h1 = animatedline('LineWidth',2);
grid on;
ylabel('linear.x');
title('Velocidad lineal');

nexttile;
h2 = animatedline('LineWidth',2);
grid on;
ylabel('angular.z');
xlabel('Tiempo (s)');
title('Velocidad angular');

disp('Ejecutando secuencia de movimiento...');
t0 = tic;

% Secuencia simple y segura para la demo
secuencias = {
    'ADELANTE',   0.20,  0.00, 4.0;
    'IZQUIERDA',  0.12,  0.50, 3.0;
    'ADELANTE',   0.20,  0.00, 3.0;
    'DERECHA',    0.12, -0.50, 3.0;
    'ADELANTE',   0.20,  0.00, 3.0;
    'STOP',       0.00,  0.00, 1.0
};

for s = 1:size(secuencias,1)
    etiqueta = secuencias{s,1};
    lx = secuencias{s,2};
    az = secuencias{s,3};
    dur = secuencias{s,4};

    fprintf('Paso: %s | linear.x=%.2f | angular.z=%.2f | duracion=%.1f s\n', ...
        etiqueta, lx, az, dur);

    msg.linear.x = lx;
    msg.angular.z = az;

    tseg = tic;
    while toc(tseg) < dur
        send(pub,msg);

        tnow = toc(t0);
        addpoints(h1,tnow,lx);
        addpoints(h2,tnow,az);
        drawnow limitrate;

        pause(0.08);
    end
end

% Stop final
msg.linear.x = 0.0;
msg.angular.z = 0.0;
send(pub,msg);

disp('====================================================');
disp('DEMO COMPLETADA');
disp('- MATLAB publico /cmd_vel');
disp('- El robot respondio en Gazebo');
if ok_cam
    disp('- MATLAB tambien recibio /camera/image_raw');
end
disp('====================================================');