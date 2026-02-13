@echo off
chcp 65001 >nul
cls

echo ================================
echo   游戏运营策划工具 - 后端服务
echo ================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.9 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安装
python --version
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
if not exist "venv\installed" (
    echo 📥 安装依赖包...
    pip install -r requirements.txt
    echo. > venv\installed
    echo.
)

REM 检查 .env 文件
if not exist ".env" (
    echo ⚠️  警告: .env 文件不存在
    echo.
    echo 请按照以下步骤配置:
    echo 1. 复制 .env.example 为 .env
    echo 2. 编辑 .env 文件，填入您的 Gemini API Key
    echo 3. 获取 API Key: https://aistudio.google.com/app/apikey
    echo.
    set /p create_env="是否现在创建 .env 文件? (y/n): "
    if /i "%create_env%"=="y" (
        copy .env.example .env
        echo ✅ 已创建 .env 文件
        echo 请编辑该文件并填入您的 API Key
        echo.
        pause
        notepad .env
    ) else (
        echo ❌ 无法启动服务，需要配置 .env 文件
        pause
        exit /b 1
    )
)

REM 启动服务
echo 🚀 启动后端服务...
echo.
python main.py

pause
