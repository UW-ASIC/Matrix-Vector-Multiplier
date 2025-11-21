#!/usr/bin/env bash
set -e

# --- Helper Function ---
install_with_brew() {
    local pkg="$1"
    if ! brew list --cask "$pkg" >/dev/null 2>&1 && ! brew list "$pkg" >/dev/null 2>&1; then
        echo "🔹 Installing $pkg via Homebrew..."
        brew install --cask "$pkg" || brew install "$pkg"
    else
        echo "✅ $pkg already installed."
    fi
}

# --- 1. Ensure Homebrew Exists ---
if ! command -v brew >/dev/null 2>&1; then
    echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh/"
    exit 1
fi

# --- 2. Install XQuartz if Missing ---
if ! command -v xquartz >/dev/null 2>&1 && ! [ -d "/Applications/Utilities/XQuartz.app" ]; then
    install_with_brew "xquartz"
    echo "⚠️ Please log out and log back in or run 'open -a XQuartz' to initialize XQuartz."
else
    echo "✅ XQuartz already installed."
fi

# --- 3. Start XQuartz if Not Running ---
if ! pgrep -x XQuartz >/dev/null; then
    echo "🔹 Starting XQuartz..."
    open -a XQuartz
    sleep 2
fi

# --- 4. Ensure Docker is Installed ---
if ! command -v docker >/dev/null 2>&1; then
    install_with_brew "docker"
    echo "⚠️ Docker installed. You may need to start Docker Desktop manually the first time."
else
    echo "✅ Docker is installed."
fi

# --- 5. Ensure Docker Daemon is Running ---
if ! docker info >/dev/null 2>&1; then
    echo "🔹 Docker is not running. Attempting to start Docker..."
    open -a Docker
    echo "⏳ Waiting for Docker to start..."
    while ! docker info >/dev/null 2>&1; do
        sleep 2
    done
fi

echo "🚀 Docker daemon is running."

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
