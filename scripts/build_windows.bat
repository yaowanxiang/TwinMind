@echo off
REM ============================================================
REM  TwinMind Windows 客户端打包脚本 (PyInstaller)
REM  产物: dist/TwinMind-Windows-x64.exe (免安装单文件)
REM ============================================================
cd /d %~dp0\..

echo [1/4] 检查 Python 环境...
where python >nul 2>nul || (echo 未找到 Python，请先安装 Python 3.10+ && exit /b 1)

echo [2/4] 安装依赖...
pip install -r requirements.txt pyinstaller >nul 2>nul

echo [3/4] 打包...
python -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name "TwinMind-Windows-x64" ^
  --add-data "twinmind/ui/web;twinmind/ui/web" ^
  --add-data "twinmind/wisdom/data;twinmind/wisdom/data" ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols.http.auto ^
  desktop_launcher.py

echo [4/4] 完成！
echo 安装包: dist\TwinMind-Windows-x64.exe
pause
