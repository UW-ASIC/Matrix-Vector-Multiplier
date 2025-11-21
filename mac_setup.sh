#!/usr/bin/env bash
set -e

# Check if XQuartz is installed
if ! command -v xquartz >/dev/null 2>&1 && ! [ -d "/Applications/Utilities/XQuartz.app" ]; then
    echo "🔹 XQuartz not found. Installing via Homebrew..."
    if ! command -v brew >/dev/null 2>&1; then
        echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh/"
        exit 1
    fi
    brew install --cask xquartz
    echo "✅ XQuartz installed. Please log out and log back in or run 'open -a XQuartz' to start it."
else
    echo "✅ XQuartz already installed."
fi

# Start XQuartz if not running
if ! pgrep -x XQuartz >/dev/null; then
    echo "🔹 Starting XQuartz..."
    open -a XQuartz
    sleep 2
fi

# Get local IP for DISPLAY
IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
[ -z "$IP" ] && IP=$(ifconfig | grep 'inet ' | awk 'NR==1{print $2}')

# Allow Docker connections
xhost +$IP >/dev/null 2>&1

# Docker image and container names
IMAGE_NAME="eda-env"
CONTAINER_NAME="eda-shell"

# Build image if missing
if [[ "$(docker images -q $IMAGE_NAME 2>/dev/null)" == "" ]]; then
    echo "🐳 Building Docker image '$IMAGE_NAME'..."
    docker build -t $IMAGE_NAME .
else
    echo "✅ Docker image '$IMAGE_NAME' already exists."
fi

# Run container
docker run -it --rm \
    -e DISPLAY=$IP:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$(pwd):/workspace" \
    -v "$HOME/.cache/nix:/root/.cache/nix" \
    -v "$HOME/.volare:/root/.volare" \
    --name $CONTAINER_NAME \
    $IMAGE_NAME nix-shell
