#!/usr/bin/env bash
# =============================================================================
# fix_xauth.sh – Sincroniza el XAUTHORITY del host al contenedor ros2_jazzy
#
# Ejecutar antes de ros2-sim si Gazebo no abre ventana.
# Agrégalo al inicio de la sesión o ejecútalo manualmente con:
#   bash ~/Documentos/Ros/container/fix_xauth.sh
# =============================================================================
set -euo pipefail

CONTAINER="ros2_jazzy"

# 1. Asegurarse que el contenedor está corriendo
podman start "$CONTAINER" 2>/dev/null || true

# 2. Permitir conexiones locales al servidor X
xhost +local: 2>/dev/null || true

# 3. Encontrar el XAUTHORITY activo de la sesión KDE/Wayland
XAUTH_FILE=""

# Primero buscar por variable de entorno
if [[ -n "${XAUTHORITY:-}" && -f "$XAUTHORITY" ]]; then
    XAUTH_FILE="$XAUTHORITY"
fi

# Si no, buscarlo en XDG_RUNTIME_DIR (KDE lo crea ahí)
if [[ -z "$XAUTH_FILE" ]]; then
    XAUTH_FILE=$(find "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}" \
                      -maxdepth 1 -name "xauth*" 2>/dev/null | head -1)
fi

# Último recurso: ~/.Xauthority
if [[ -z "$XAUTH_FILE" || ! -f "$XAUTH_FILE" ]]; then
    XAUTH_FILE="$HOME/.Xauthority"
fi

if [[ ! -f "$XAUTH_FILE" ]]; then
    echo "❌ No se encontró ningún archivo XAUTHORITY. ¿Está activa la sesión gráfica?"
    exit 1
fi

echo "📋 XAUTHORITY origen: $XAUTH_FILE"

# 4. Copiar al contenedor
podman cp "$XAUTH_FILE" "$CONTAINER:/root/.Xauthority"
echo "✅ /root/.Xauthority actualizado en el contenedor '$CONTAINER'"

# 5. Verificar con xdpyinfo
echo ""
echo "🔍 Verificando acceso X11 desde el contenedor..."
podman exec "$CONTAINER" bash -c '
    export DISPLAY=:0
    export XAUTHORITY=/root/.Xauthority
    xdpyinfo 2>&1 | head -3 && echo "✅ X11 OK" || echo "❌ X11 falló"
'
