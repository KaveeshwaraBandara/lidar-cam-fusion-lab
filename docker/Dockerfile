# =============================================================================
# lidar-cam-fusion-lab :: development image
# Base: ROS 2 Jazzy (Ubuntu 24.04 Noble) — Tier 1, LTS until May 2029
# =============================================================================
# Build:  docker compose build
# Run:    docker compose up -d && docker compose exec fusion bash
# =============================================================================

ARG ROS_DISTRO=jazzy
FROM osrf/ros:${ROS_DISTRO}-desktop

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# ---- Locale (UTF-8 required by ROS 2 in minimal containers) ------------------
RUN apt-get update && apt-get install -y --no-install-recommends locales \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# ---- System / build deps -----------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git wget curl unzip \
        python3-pip python3-dev python3-venv \
        ros-dev-tools \
        # OpenCV / Open3D / GUI runtime libs
        libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
        libusb-1.0-0 ffmpeg \
        # ROS perception bridges
        ros-${ROS_DISTRO}-cv-bridge \
        ros-${ROS_DISTRO}-vision-opencv \
        ros-${ROS_DISTRO}-pcl-ros \
        ros-${ROS_DISTRO}-tf-transformations \
        ros-${ROS_DISTRO}-rviz2 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

# ---- Python deps -------------------------------------------------------------
ENV PIP_DEFAULT_TIMEOUT=300
COPY docker/requirements.txt /tmp/requirements.txt
# Pin numpy<2.0 FIRST so opencv/open3d/torch all build against it.
RUN pip3 install --no-cache-dir --break-system-packages \
        --retries 10 --timeout 300 "numpy<2.0" \
    && pip3 install --no-cache-dir --break-system-packages \
        --retries 10 --timeout 300 \
        --index-url https://download.pytorch.org/whl/cpu \
        torch torchvision \
    && pip3 install --no-cache-dir --break-system-packages \
        --retries 10 --timeout 300 ultralytics \
    && pip3 install --no-cache-dir --break-system-packages \
        --retries 10 --timeout 300 -r /tmp/requirements.txt

# ---- Non-root user (matches typical host UID 1000) ---------------------------
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=1000
# Ubuntu 24.04 base already has a uid-1000 "ubuntu" user; reuse or create.
RUN if id -u ${USER_UID} >/dev/null 2>&1; then \
        existing=$(id -un ${USER_UID}); \
        if [ "$existing" != "${USERNAME}" ]; then usermod -l ${USERNAME} -d /home/${USERNAME} -m ${existing} || true; fi; \
    else \
        groupadd --gid ${USER_GID} ${USERNAME} && \
        useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}; \
    fi \
    && apt-get update && apt-get install -y --no-install-recommends sudo \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && rm -rf /var/lib/apt/lists/*

# ---- Auto-source ROS + workspace --------------------------------------------
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo "[ -f /workspace/ros2_ws/install/setup.bash ] && source /workspace/ros2_ws/install/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo "export PYTHONPATH=/workspace/src:\$PYTHONPATH" >> /home/${USERNAME}/.bashrc

USER ${USERNAME}
WORKDIR /workspace

COPY docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
