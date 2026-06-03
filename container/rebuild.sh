#!/usr/bin/env bash
# =============================================================================
# rebuild.sh  – Recompila el workspace dentro del contenedor
# Uso desde Fedora: bash container/rebuild.sh
# =============================================================================
set -euo pipefail

CONTAINER_NAME="ros2_jazzy"

podman start "$CONTAINER_NAME" 2>/dev/null || true

podman exec "$CONTAINER_NAME" bash -c '
  set -eo pipefail
  source /opt/ros/jazzy/setup.bash
  cd /root/Ros
  rm -rf build install log
  colcon build --packages-select robot_control --symlink-install
  echo ""
  echo "✅ Recompilación completa."
  echo "   source /root/Ros/install/setup.bash → ya incluido en .bashrc del contenedor"
'
