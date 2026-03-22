"""FastAPI 主入口"""
import os
import re
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import asyncio

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TEMP_DIR, RESULTS_DIR, get_language_name
from services.csv_parser import parse_csv, detect_chinese_columns
from services.storage import storage
from agents.orchestrator import orchestrator

app = FastAPI(
    title="CSV 多语言翻译 Agent",
    description="基于 Chat 对话的 CSV 多语言翻译服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
os.makedirs(RESULTS_DIR, exist_ok=True)
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")


# === 请求/响应模型 ===

class StartTranslationRequest(BaseModel):
    """开始翻译请求"""
    task_id: str
    columns_to_translate: List[str]
    target_languages: List[str]

class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    total_rows: int
    total_batches: int
    completed_batches: int
    progress_percent: float
    current_batch: int
    message: str
    target_languages: List[str]
    columns_to_translate: List[str]
    started_at: str
    completed_at: Optional[str] = None
    errors: List[str] = []

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user, assistant
    content: str
    timestamp: str = ""


# === 存储对话历史 ===

chat_histories = {}  # task_id -> List[ChatMessage]
task_data = {}  # task_id -> DataFrame


# === API 接口 ===

@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "CSV 多语言翻译 Agent 服务运行中"}


@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """上传 CSV 文件"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="请上传 CSV 文件")

    # 保存文件
    task_id, filepath = storage.save_upload(await file.read(), file.filename)

    # 解析 CSV
    try:
        df, stats = parse_csv(filepath)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV 解析失败: {str(e)}")

    # 存储数据
    task_data[task_id] = df
    chat_histories[task_id] = []

    # 添加助手消息
    assistant_msg = f"""📄 已收到文件 {file.filename}

• 数据量：{stats['total_rows']} 条
• 列数：{stats['total_columns']} 列
• 检测到中文列：{', '.join(stats['chinese_columns']) if stats['chinese_columns'] else '未检测到'}

请确认：
1. 要翻译哪些列？
2. 翻译成哪些语言？（支持：英语、日语、韩语、法语、德语、西班牙语、俄语）"""

    chat_histories[task_id].append(ChatMessage(
        role="assistant",
        content=assistant_msg,
        timestamp=datetime.now().isoformat()
    ))

    return {
        "task_id": task_id,
        "stats": stats,
        "chat_history": [msg.dict() for msg in chat_histories[task_id]]
    }


@app.post("/api/chat")
async def chat(message: str, task_id: str):
    """处理对话消息"""
    if task_id not in task_data:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 添加用户消息
    chat_histories[task_id].append(ChatMessage(
        role="user",
        content=message,
        timestamp=datetime.now().isoformat()
    ))

    df = task_data[task_id]
    chinese_columns = detect_chinese_columns(df)

    # 解析用户意图 - 提取语言
    languages = []

    # 预设语言检测（代码和中文名）
    preset_languages = {
        "en": ["英语", "英文", "en"],
        "ja": ["日语", "日文", "ja"],
        "ko": ["韩语", "韩文", "ko"],
        "fr": ["法语", "法文", "fr"],
        "de": ["德语", "德文", "de"],
        "es": ["西班牙语", "es"],
        "ru": ["俄语", "俄文", "ru"],
        "pt": ["葡萄牙语", "pt"],
        "it": ["意大利语", "it"],
        "ar": ["阿拉伯语", "ar"],
        "th": ["泰语", "th"],
        "vi": ["越南语", "vi"],
    }

    user_input_lower = message.lower()
    for code, keywords in preset_languages.items():
        if any(kw in user_input_lower for kw in keywords):
            languages.append(code)

    # 如果没有检测到预设语言，尝试从"翻译成XXX"格式中提取
    if not languages:
        # 匹配 "翻译成xxx" 或 "翻译为xxx"
        match = re.search(r'翻译[成为](.+?)(?:和|、|$)', message)
        if match:
            lang_text = match.group(1).strip()
            # 按分隔符拆分多个语言
            lang_list = re.split(r'[、和,，]', lang_text)
            for lang in lang_list:
                lang = lang.strip()
                if lang:
                    languages.append(lang)

    # 如果仍然没有语言，尝试提取整个目标语言部分
    if not languages:
        match = re.search(r'翻译[成为](.+)$', message)
        if match:
            lang_text = match.group(1).strip()
            lang_list = re.split(r'[、和,，]', lang_text)
            for lang in lang_list:
                lang = lang.strip()
                if lang:
                    languages.append(lang)

    # 如果没有检测到语言，返回提示
    if not languages:
        assistant_msg = """请指定要翻译的目标语言。

支持的语言：
• 英语、日语、韩语、法语、德语、西班牙语、俄语
• 葡萄牙语、意大利语、阿拉伯语、泰语、越南语
• 或输入任意其他语言名称

例如："翻译成英语和日语" 或 "翻译成荷兰语" """
    else:
        # 开始翻译
        assistant_msg = f"""⏳ 开始翻译...

• 翻译列：{', '.join(chinese_columns)}
• 目标语言：{', '.join(languages)}
• 数据量：{len(df)} 条

正在处理中，请稍候..."""

        chat_histories[task_id].append(ChatMessage(
            role="assistant",
            content=assistant_msg,
            timestamp=datetime.now().isoformat()
        ))

        # 启动翻译任务（后台）
        asyncio.create_task(
            orchestrator.start_translation(
                task_id=task_id,
                df=df,
                columns_to_translate=chinese_columns,
                target_languages=languages,
                progress_callback=lambda p: update_chat_progress(task_id, p)
            )
        )

        return {
            "task_id": task_id,
            "chat_history": [msg.dict() for msg in chat_histories[task_id]],
            "translation_started": True,
            "target_languages": languages
        }

    # 添加助手消息
    chat_histories[task_id].append(ChatMessage(
        role="assistant",
        content=assistant_msg,
        timestamp=datetime.now().isoformat()
    ))

    return {
        "task_id": task_id,
        "chat_history": [msg.dict() for msg in chat_histories[task_id]],
        "translation_started": False
    }


async def update_chat_progress(task_id: str, progress):
    """更新翻译进度到对话"""
    msg = f"⏳ 翻译进度：{progress.progress_percent:.1f}% ({progress.completed_batches}/{progress.total_batches} 批次)"

    if progress.status == "completed":
        msg = f"""✅ 翻译完成！

• 处理数据：{progress.total_rows} 条
• 批次数：{progress.total_batches}
• 耗时：{calculate_duration(progress.started_at, progress.completed_at)}

📊 预览结果：/result/{task_id}
📥 下载 CSV：/download/{task_id}"""

    chat_histories[task_id].append(ChatMessage(
        role="assistant",
        content=msg,
        timestamp=datetime.now().isoformat()
    ))


def calculate_duration(start: str, end: str) -> str:
    """计算耗时"""
    try:
        start_time = datetime.fromisoformat(start)
        end_time = datetime.fromisoformat(end)
        seconds = (end_time - start_time).total_seconds()
        if seconds < 60:
            return f"{int(seconds)} 秒"
        return f"{int(seconds / 60)} 分 {int(seconds % 60)} 秒"
    except:
        return "未知"


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """获取任务状态"""
    progress = orchestrator.get_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskStatusResponse(
        task_id=progress.task_id,
        status=progress.status,
        total_rows=progress.total_rows,
        total_batches=progress.total_batches,
        completed_batches=progress.completed_batches,
        progress_percent=progress.progress_percent,
        current_batch=progress.current_batch,
        message=progress.message,
        target_languages=progress.target_languages,
        columns_to_translate=progress.columns_to_translate,
        started_at=progress.started_at,
        completed_at=progress.completed_at,
        errors=progress.errors
    )


@app.get("/api/chat/{task_id}")
async def get_chat_history(task_id: str):
    """获取对话历史"""
    if task_id not in chat_histories:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "task_id": task_id,
        "chat_history": [msg.dict() for msg in chat_histories[task_id]]
    }


@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """下载翻译结果 CSV"""
    csv_path = storage.get_result_csv_path(task_id)
    if not csv_path:
        raise HTTPException(status_code=404, detail="结果文件不存在")

    return FileResponse(
        path=csv_path,
        filename=f"translated_{task_id}.csv",
        media_type="text/csv"
    )


@app.get("/result/{task_id}", response_class=HTMLResponse)
async def view_result(task_id: str):
    """查看翻译结果预览"""
    html_path = storage.get_result_html_path(task_id)
    if not html_path:
        return HTMLResponse(content="<h1>结果未就绪，请稍后再试</h1>", status_code=404)

    with open(html_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
