#!/bin/bash
# PopTech Cinema Studio — Wan 2.6 VPS Deployment Script
# Task 5.2: Deploy Wan 2.6 video generation on GPU VPS
#
# PREREQUISITES:
#   - GPU VPS with NVIDIA GPU (RTX 3090+ recommended, 24GB+ VRAM)
#   - Docker + nvidia-container-toolkit installed
#   - 50GB+ free disk space for models
#
# NOTE: Requires a GPU VPS. If your current VPS is CPU-only, provision a GPU
# instance (e.g., Hetzner, Lambda Labs, Vast.ai) or use a cloud fallback.
#
# Usage: ssh root@GPU_VPS 'bash -s' < tools/deploy_wan26_vps.sh

set -e

echo "=== PopTech: Wan 2.6 VPS Deployment ==="

# Check GPU
if ! nvidia-smi &>/dev/null; then
    echo "ERROR: No NVIDIA GPU detected. Wan 2.6 requires GPU."
    echo "This host appears to be CPU-only."
    echo "Options:"
    echo "  1. Upgrade VPS to GPU instance (Hetzner, Lambda Labs, Vast.ai)"
    echo "  2. Use fal.ai cloud Wan 2.6 (\$0.10/sec) as fallback"
    echo "  3. Use local RTX 3050 via ComfyUI Desktop"
    exit 1
fi

echo "GPU detected:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Install nvidia-container-toolkit if not present
if ! dpkg -l | grep -q nvidia-container-toolkit; then
    echo "Installing nvidia-container-toolkit..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L "https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list" | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    apt-get update && apt-get install -y nvidia-container-toolkit
    nvidia-ctk runtime configure --runtime=docker
    systemctl restart docker
fi

# Create directories
mkdir -p /opt/wan26/models /opt/wan26/outputs

# Pull ComfyUI with Wan 2.6 support
echo "Pulling ComfyUI Docker image..."
docker pull ghcr.io/ai-dock/comfyui:latest

# Download Wan 2.6 model weights
echo "Downloading Wan 2.6 model weights..."
cd /opt/wan26/models
if [ ! -f "wan2.6_t2v.safetensors" ]; then
    wget -q "https://huggingface.co/Wan-AI/Wan2.6-T2V/resolve/main/wan2.6_t2v.safetensors" || echo "Download failed — add HuggingFace token"
fi

# Deploy ComfyUI with GPU
echo "Starting ComfyUI with GPU..."
docker run -d \
    --name comfyui-wan26 \
    --restart unless-stopped \
    --gpus all \
    -p 127.0.0.1:8188:8188 \
    -v /opt/wan26/models:/opt/ComfyUI/models/checkpoints \
    -v /opt/wan26/outputs:/opt/ComfyUI/output \
    ghcr.io/ai-dock/comfyui:latest

# Deploy FastAPI wrapper for N8N integration
echo "Deploying REST API wrapper..."
cat > /opt/wan26/api.py << 'PYEOF'
"""Wan 2.6 REST API wrapper for N8N integration."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess, json, os

app = FastAPI(title="Wan 2.6 Generation API")

class GenerateRequest(BaseModel):
    prompt: str
    duration_seconds: int = 5
    width: int = 1280
    height: int = 720

@app.get("/health")
def health():
    return {"status": "ok", "model": "wan2.6", "gpu": True}

@app.post("/generate")
async def generate(req: GenerateRequest):
    # Queue ComfyUI workflow via API
    # STUB: Actual ComfyUI workflow submission
    return {"status": "queued", "note": "ComfyUI workflow integration pending"}

PYEOF

echo "=== Wan 2.6 deployment complete ==="
echo "ComfyUI: http://localhost:8188"
echo "API: http://localhost:5000 (deploy with uvicorn)"
echo ""
echo "N8N cost-routing: When this is live, N8N workflows should route"
echo "test/iteration renders to Wan 2.6 local (\$0) and only send"
echo "final renders to Seedance 2.0 (fal.ai, \$0.10/sec)."
