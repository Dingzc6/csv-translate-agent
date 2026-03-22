#!/bin/bash

echo "=========================================="
echo "  CSV 多语言翻译 Agent 启动脚本"
echo "=========================================="

# 创建必要目录
mkdir -p temp results

# 启动后端
echo ""
echo "🚀 启动后端服务..."
cd backend
pip install -r requirements.txt -q 2>/dev/null
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "🎨 启动前端服务..."
cd frontend
npm install --silent 2>/dev/null
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "  ✅ 服务已启动"
echo "=========================================="
echo ""
echo "  📦 后端 API: http://localhost:8000"
echo "  🌐 前端界面: http://localhost:3000"
echo "  📖 API 文档: http://localhost:8000/docs"
echo ""
echo "  按 Ctrl+C 停止服务"
echo "=========================================="

# 等待进程
wait $BACKEND_PID $FRONTEND_PID
