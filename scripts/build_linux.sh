#!/usr/bin/env bash
# TwinMind Linux 客户端打包脚本 (PyInstaller)
# 产物: dist/TwinMind-Linux-$(uname -m)
set -e
cd "$(dirname "$0")/.."

echo "[1/4] 检查 Python..."
command -v python3 >/dev/null || { echo "未找到 python3"; exit 1; }

echo "[2/4] 安装依赖..."
python3 -m pip install -r requirements.txt pyinstaller

echo "[3/4] 打包..."
ARCH=$(uname -m)
python3 -m PyInstaller \
  --noconfirm \
  --onefile \
  --windowed \
  --name "TwinMind-Linux-${ARCH}" \
  --add-data "twinmind/ui/web:twinmind/ui/web" \
  --add-data "twinmind/wisdom/data:twinmind/wisdom/data" \
  --hidden-import uvicorn.logging \
  --hidden-import uvicorn.loops.auto \
  desktop_launcher.py

echo "[4/4] 完成！"
echo "可执行文件: dist/TwinMind-Linux-${ARCH}"
