#!/bin/bash
# 一人公司快速启动脚本

cd "$(dirname "$0")"

echo "🏢 一人公司 AI Agent 系统"
echo "=========================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt

# 创建必要目录
mkdir -p data logs

# 检查API配置
if [ ! -f "config/api_keys.yaml" ]; then
    echo "⚠️  未找到API配置文件"
    echo "正在从示例文件创建..."
    cp config/api_keys.yaml.example config/api_keys.yaml
    echo "✅ 已创建 config/api_keys.yaml"
    echo "📝 请编辑此文件填入你的API密钥"
fi

echo ""
echo "🚀 启动系统..."
echo ""

python3 main.py
