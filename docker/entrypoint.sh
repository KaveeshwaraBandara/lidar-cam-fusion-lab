#!/usr/bin/env bash
set -e
# Source ROS 2 and (if built) the local workspace, then exec the command.
source "/opt/ros/${ROS_DISTRO}/setup.bash"
if [ -f /workspace/ros2_ws/install/setup.bash ]; then
    source /workspace/ros2_ws/install/setup.bash
fi
exec "$@"
