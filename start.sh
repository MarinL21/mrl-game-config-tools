#!/bin/bash

# 游戏运营策划工具 - 后端服务启动脚本

echo "================================"
echo "  游戏运营策划工具 - 后端服务"
echo "================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.9 或更高版本"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if [ ! -f "venv/installed" ]; then
    echo "📥 安装依赖包..."
    pip install -r requirements.txt
    touch venv/installed
    echo ""
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo ""
    echo "请按照以下步骤配置:"
    echo "1. 复制 .env.example 为 .env"
    echo "   cp .env.example .env"
    echo ""
    echo "2. 编辑 .env 文件，填入您的 Gemini API Key"
    echo "   nano .env"
    echo ""
    echo "3. 获取 API Key: https://aistudio.google.com/app/apikey"
    echo ""
    read -p "是否现在创建 .env 文件? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
        echo "请编辑该文件并填入您的 API Key"
        echo ""
        read -p "按 Enter 键打开编辑器..."
        ${EDITOR:-nano} .env
    else
        echo "❌ 无法启动服务，需要配置 .env 文件"
        exit 1
    fi
fi

# 运行测试（可选）
echo "🧪 是否运行 API 测试? (y/n)"
read -t 5 -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "运行测试脚本..."
    python3 test_api.py &
    TEST_PID=$!
fi

# 启动服务
echo "🚀 启动后端服务..."
echo ""
python3 main.py

# 清理
if [ ! -z "$TEST_PID" ]; then
    kill $TEST_PID 2>/dev/null
fi
