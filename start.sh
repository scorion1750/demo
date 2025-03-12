#!/bin/bash

# 加载环境变量
source .env 2>/dev/null || echo "No .env file found"

# 设置默认值
PORT=${API_PORT:-8001}

echo "Starting API server on 0.0.0.0:$PORT..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload 