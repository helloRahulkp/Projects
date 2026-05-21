#!/usr/bin/env bash
# =============================================================================
# macOS / Linux Setup Script — AI Currency Detection System v2.0
# =============================================================================

set -e

echo "============================================================"
echo " AI Currency Detection System v2.0 — macOS/Linux Setup"
echo "============================================================"
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed."
    echo "Install from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo "[OK] Docker detected: $(docker --version)"

# Check docker compose
if ! docker compose version &> /dev/null; then
    echo "[ERROR] Docker Compose not found. Update Docker Desktop."
    exit 1
fi
echo "[OK] Docker Compose detected"

# Copy .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[OK] Created .env from .env.example"
fi

echo
echo "[INFO] Building and starting all services..."
echo "[INFO] First build may take 5–10 minutes..."
echo

docker compose up --build
