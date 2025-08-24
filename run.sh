#!/bin/bash

# Oracle Cloud VPS 网络测试工具启动脚本

echo "🚀 启动 Oracle Cloud VPS 网络测试工具..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.9"

if [[ $(echo "$python_version >= $required_version" | bc) -eq 0 ]]; then
    echo "❌ 错误: 需要 Python $required_version 或更高版本，当前版本: $python_version"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📚 检查并安装依赖..."
pip install -q -r requirements.txt

# 启动应用
echo "✅ 启动服务器..."
echo "🌐 请在浏览器中访问: http://localhost:5001"
echo "📌 按 Ctrl+C 停止服务器"
echo ""

python3 app.py