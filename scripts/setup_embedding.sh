#!/bin/bash
# 一键安装本地 Embedding 服务
# 用法: bash setup_embedding.sh

set -e

echo "=== Agent Memory System - Embedding 服务安装脚本 ==="

# 检查 conda
if ! command -v conda &> /dev/null; then
    echo "❌ 未找到 conda，请先安装 Miniconda 或 Anaconda"
    exit 1
fi

ENV_NAME="agent-memory"
PYTHON_VERSION="3.11"

# 创建环境
echo "📦 创建 conda 环境: $ENV_NAME"
conda create -n $ENV_NAME python=$PYTHON_VERSION -y
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# 安装依赖
echo "📥 安装依赖: sentence-transformers, fastapi, uvicorn"
pip install sentence-transformers fastapi uvicorn

# 下载模型（首次运行自动下载，这里预热）
echo "🤖 预下载 BGE-small-zh-v1.5 模型..."
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"

echo ""
echo "✅ 安装完成！"
echo ""
echo "启动服务:"
echo "  conda activate $ENV_NAME"
echo "  python embedding_server.py"
echo ""
echo "服务地址: http://localhost:8080/v1"