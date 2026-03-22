# CSV 多语言翻译 Agent

基于 Chat 对话的 CSV 多语言翻译服务，支持 Batch 分片处理和大模型校验，避免翻译幻觉问题。

## 功能特点

- **💬 Chat 对话交互**：自然语言指定翻译需求
- **📊 Batch 分片处理**：每 20 条一组，支持断点续传
- **✅ 大模型校验**：翻译后自动校验，检测幻觉问题
- **🌍 多语言支持**：英语、日语、韩语、法语、德语、西班牙语、俄语
- **🔄 实时进度**：翻译过程中实时展示进度
- **📄 结果预览**：生成可访问的预览 URL

## 技术架构

```
前端 (React + Tailwind)
    ↓
后端 (FastAPI)
    ↓
Agent 核心层
├── Orchestrator (调度器)
├── Translator (翻译 Agent)
└── Validator (校验 Agent)
```

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

### 2. 启动服务

```bash
# 方式一：使用启动脚本
./start.sh

# 方式二：分别启动
# 终端1 - 后端
cd backend && python main.py

# 终端2 - 前端
cd frontend && npm start
```

### 3. 访问应用

- 前端界面：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 使用流程

1. **上传 CSV**：拖拽或点击上传含有中文列的 CSV 文件
2. **指定语言**：在对话框中输入目标语言（如："翻译成英语和日语"）
3. **等待翻译**：系统自动 Batch 处理并校验
4. **获取结果**：预览结果或下载 CSV

## 配置说明

编辑 `backend/config.py`：

```python
# LLM 配置
LLM_API_URL = "https://ai.t8star.cn/v1/chat/completions"
LLM_MODEL = "gpt-5.4"

# Batch 配置
BATCH_SIZE = 20  # 每批处理条数
MAX_RETRY = 3    # 最大重试次数
```

## 测试文件

项目包含测试数据：`temp/test_data.csv`（20 条商品数据）

## 云端部署

### Vercel 部署前端

```bash
cd frontend
npm run build
vercel --prod
```

### Railway 部署后端

```bash
railway init
railway up
```

## 项目结构

```
csv-translator-agent/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置文件
│   ├── agents/
│   │   ├── orchestrator.py  # 调度 Agent
│   │   ├── translator.py    # 翻译 Agent
│   │   └── validator.py     # 校验 Agent
│   └── services/
│       ├── csv_parser.py    # CSV 解析
│       ├── batch_processor.py
│       └── storage.py
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── components/Chat.js
│   └── package.json
├── temp/                    # 临时文件
├── results/                 # 翻译结果
└── start.sh                 # 启动脚本
```

## License

MIT
