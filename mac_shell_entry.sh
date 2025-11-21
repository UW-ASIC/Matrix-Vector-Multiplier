#!/usr/bin/env bash
set -e
IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
[ -z "$IP" ] && IP=$(ifconfig | grep 'inet ' | awk 'NR==1{print $2}')

# Allow Docker connections
xhost +$IP >/dev/null 2>&1

# Docker image and container names
IMAGE_NAME="eda-env"
CONTAINER_NAME="eda-shell"

docker run -it --rm \
    -e DISPLAY=$IP:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$(pwd):/workspace" \
    -v "$HOME/.cache/nix:/root/.cache/nix" \
    -v "$HOME/.volare:/root/.volare" \
    --name $CONTAINER_NAME \
    $IMAGE_NAME nix-shell