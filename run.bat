@echo off
REM 公式识别工具启动脚本
REM 激活p2t环境并运行应用

cd /d %~dp0
echo tool is loading, please wait...
echo.

D:/anaconda/envs/p2t/python.exe app.py

if errorlevel 1 (
    echo.
    echo Failed to start the tool!
    echo Please ensure the p2t environment is correctly configured and all dependencies are installed.
    pause
    exit /b 1
)
