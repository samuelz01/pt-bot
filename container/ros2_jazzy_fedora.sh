#!/usr/bin/env bash
# =============================================================================
# ros2_jazzy_fedora.sh
# Configura un contenedor Podman (Ubuntu 24.04) con ROS 2 Jazzy + Gazebo
# para el proyecto robot_control en Fedora 44.
#
# Uso: bash container/ros2_jazzy_fedora.sh
# =============================================================================
set -euo pipefail

# ── Colores para salida legible ───────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
info() { echo -e "${CYAN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

CONTAINER_NAME="ros2_jazzy"
WORKSPACE="$HOME/Documentos/Ros"

# ── 0. Verificaciones previas ─────────────────────────────────────────────────
info "Verificando entorno Fedora..."
command -v podman >/dev/null 2>&1 || fail "Podman no encontrado. Instálalo con: sudo dnf install -y podman"
ok "Podman $(podman --version | awk '{print $3}') disponible."

[[ -d "$WORKSPACE/src/robot_control" ]] || \
  fail "Directorio del proyecto no encontrado: $WORKSPACE/src/robot_control"
ok "Proyecto encontrado en $WORKSPACE"

# ── 1. Eliminar contenedor previo si existe ───────────────────────────────────
if podman container exists "$CONTAINER_NAME" 2>/dev/null; then
  warn "Contenedor '$CONTAINER_NAME' ya existe. Eliminando..."
  podman rm -f "$CONTAINER_NAME"
  ok "Contenedor anterior eliminado."
fi

# ── 2. Preparar acceso XWayland ──────────────────────────────────────────────
info "Configurando acceso al display (XWayland via DISPLAY=:0)..."
xhost +local: 2>/dev/null || warn "xhost no disponible"
ok "Display configurado: DISPLAY=${DISPLAY:-:0}"

# Encontrar el XAUTHORITY activo de la sesión
XAUTH_FILE=""
if [[ -n "${XAUTHORITY:-}" && -f "${XAUTHORITY:-}" ]]; then
  XAUTH_FILE="$XAUTHORITY"
fi
if [[ -z "$XAUTH_FILE" ]]; then
  XAUTH_FILE=$(find "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}" \
                    -maxdepth 1 -name "xauth*" 2>/dev/null | head -1)
fi
if [[ -z "$XAUTH_FILE" || ! -f "$XAUTH_FILE" ]]; then
  XAUTH_FILE="$HOME/.Xauthority"
fi
info "XAUTHORITY: $XAUTH_FILE"

# ── 3. Crear contenedor Ubuntu 24.04 ─────────────────────────────────────────
info "Creando contenedor Ubuntu 24.04 (ROS 2 Jazzy base)..."
podman run -d \
  --name "$CONTAINER_NAME" \
  --network=host \
  --env DISPLAY=":0" \
  --env XAUTHORITY="/root/.Xauthority" \
  --env QT_QPA_PLATFORM=xcb \
  --env QT_X11_NO_MITSHM=1 \
  --env GZ_IP=127.0.0.1 \
  --env IGN_IP=127.0.0.1 \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --volume "$WORKSPACE:/root/Ros:rw" \
  --device /dev/dri \
  --security-opt label=disable \
  docker.io/library/ubuntu:24.04 \
  sleep infinity

# Copiar el XAUTHORITY del host al contenedor
podman cp "$XAUTH_FILE" "$CONTAINER_NAME:/root/.Xauthority"
ok "Contenedor '$CONTAINER_NAME' creado. XAUTHORITY copiado."

# ── 4. Instalar ROS 2 Jazzy + Gazebo Harmonic ────────────────────────────────
info "Instalando ROS 2 Jazzy + Gazebo Harmonic (puede tardar 5-15 min)..."
podman exec "$CONTAINER_NAME" bash -c '
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

# Herramientas base
apt-get update -q
apt-get install -y --no-install-recommends \
  curl gnupg2 lsb-release software-properties-common \
  ca-certificates locales tzdata

# Locale UTF-8
locale-gen en_US en_US.UTF-8
update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# ── Repositorio ROS 2 ──────────────────────────────────────────────────────
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  > /etc/apt/sources.list.d/ros2.list

# ── Repositorio Gazebo Harmonic ────────────────────────────────────────────
curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
  | gpg --dearmor -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
  http://packages.osrfoundation.org/gazebo/ubuntu-stable $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  > /etc/apt/sources.list.d/gazebo-stable.list

apt-get update -q

# ── Paquetes ROS 2 Jazzy + libGL + herramientas display ───────────────────
apt-get install -y \
  ros-jazzy-desktop \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-interfaces \
  ros-jazzy-sensor-msgs \
  ros-jazzy-geometry-msgs \
  ros-jazzy-teleop-twist-keyboard \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-pip \
  git vim wget \
  libgl1 libgl1-mesa-dri libglx-mesa0 \
  mesa-utils x11-utils x11-apps

cat >> /root/.bashrc << 'CONTAINER_ENV'
source /opt/ros/jazzy/setup.bash
source /root/Ros/install/setup.bash 2>/dev/null || true
# ── Display: XWayland via xcb (Gazebo GUI fix) ────────────────────────────
export DISPLAY=:0
export XAUTHORITY=/root/.Xauthority
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
unset WAYLAND_DISPLAY
export GZ_IP=127.0.0.1
export IGN_IP=127.0.0.1
CONTAINER_ENV

echo "✅ Instalación ROS 2 Jazzy + Gazebo Harmonic completada."
'
ok "ROS 2 Jazzy + Gazebo Harmonic instalados."

# ── 5. Inicializar rosdep ─────────────────────────────────────────────────────
info "Inicializando rosdep..."
podman exec "$CONTAINER_NAME" bash -c '
  source /opt/ros/jazzy/setup.bash
  rosdep init 2>/dev/null || true
  rosdep update
' 2>/dev/null || warn "rosdep init ya fue ejecutado anteriormente."
ok "rosdep listo."

# ── 6. Compilar el workspace ──────────────────────────────────────────────────
info "Compilando workspace robot_control..."
podman exec "$CONTAINER_NAME" bash -c '
  set -eo pipefail
  source /opt/ros/jazzy/setup.bash
  cd /root/Ros
  rm -rf build install log
  colcon build --packages-select robot_control --symlink-install
  echo "✅ Compilación exitosa."
'
ok "Workspace compilado."

# ── 7. Validación final ───────────────────────────────────────────────────────
info "Validando instalación..."
podman exec "$CONTAINER_NAME" bash -c '
  set -eo pipefail
  source /opt/ros/jazzy/setup.bash
  source /root/Ros/install/setup.bash
  echo "ROS_DISTRO: $ROS_DISTRO"
  ros2 pkg list | grep robot_control && echo "✅ paquete robot_control visible"
'
ok "Validación completa."

# ── 8. Crear/actualizar alias convenientes ────────────────────────────────────
ALIAS_FILE="$HOME/.bashrc"

# Limpiar alias anteriores para actualizarlos
sed -i '/# ros2_jazzy_fedora aliases/,/^ALIASES$/d' "$ALIAS_FILE" 2>/dev/null || true
sed -i '/alias ros2-[[:alnum:]_-]*=/d' "$ALIAS_FILE" 2>/dev/null || true

cat >> "$ALIAS_FILE" << 'ALIASES'

# ros2_jazzy_fedora aliases
alias ros2-xauth='bash ~/Documentos/Ros/container/fix_xauth.sh'
alias ros2-start='podman start ros2_jazzy 2>/dev/null || true && bash ~/Documentos/Ros/container/fix_xauth.sh'
alias ros2-sim='bash ~/Documentos/Ros/container/fix_xauth.sh && podman exec -it ros2_jazzy bash -c "export DISPLAY=:0; export XAUTHORITY=/root/.Xauthority; export QT_QPA_PLATFORM=xcb; export QT_X11_NO_MITSHM=1; unset WAYLAND_DISPLAY; export GZ_IP=127.0.0.1; export IGN_IP=127.0.0.1; source /opt/ros/jazzy/setup.bash && source /root/Ros/install/setup.bash && ros2 launch robot_control sim_car.launch.py"'
alias ros2-shell='podman exec -it ros2_jazzy bash'
alias ros2-topics='podman exec ros2_jazzy bash -c "source /opt/ros/jazzy/setup.bash && source /root/Ros/install/setup.bash && ros2 topic list"'
ALIASES
ok "Alias actualizados en ~/.bashrc"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         ENTORNO ROS 2 JAZZY LISTO EN FEDORA 44             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}Para ejecutar el proyecto:${NC}"
echo ""
echo -e "  ${YELLOW}# Terminal 1 – Simulación${NC}"
echo -e "  ros2-sim"
echo ""
echo -e "  ${YELLOW}# Shell dentro del contenedor${NC}"
echo -e "  ros2-shell"
echo ""
echo -e "  ${YELLOW}# Ver topics ROS${NC}"
echo -e "  ros2-topics"
echo ""
echo -e "  ${CYAN}Recarga tus alias con:${NC} source ~/.bashrc"
echo ""
