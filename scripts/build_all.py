#!/usr/bin/env python3
"""TwinMind 跨平台一键打包 — 自动检测当前系统并调用对应构建脚本。"""
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def main():
    system = platform.system().lower()
    print(f"检测到系统: {system}")
    if system == "windows":
        subprocess.run(["cmd", "/c", str(ROOT / "scripts" / "build_windows.bat")], check=False)
    elif system == "darwin":
        subprocess.run(["bash", str(ROOT / "scripts" / "build_macos.sh")], check=False)
    elif system == "linux":
        subprocess.run(["bash", str(ROOT / "scripts" / "build_linux.sh")], check=False)
    else:
        print(f"暂不支持的系统: {system}")
        sys.exit(1)


if __name__ == "__main__":
    main()
