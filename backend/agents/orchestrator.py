"""调度 Agent - 协调整个翻译流程"""
import asyncio
from typing import List, Optional, Callable
from dataclasses import dataclass, field
import pandas as pd
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BATCH_SIZE, MAX_RETRY
from services.batch_processor import BatchProcessor, Batch
from services.storage import storage
from agents.translator import translator_agent
from agents.validator import validator_agent

@dataclass
class TaskProgress:
    """任务进度"""
    task_id: str
    status: str = "pending"  # pending, processing, completed, failed
    total_rows: int = 0
    total_batches: int = 0
    completed_batches: int = 0
    current_batch: int = 0
    progress_percent: float = 0.0
    target_languages: List[str] = field(default_factory=list)
    columns_to_translate: List[str] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    message: str = ""
    errors: List[str] = field(default_factory=list)

class Orchestrator:
    """调度器 - 协调翻译和校验流程"""

    def __init__(self):
        self.tasks: dict = {}  # task_id -> TaskProgress
        self.batch_processors: dict = {}  # task_id -> BatchProcessor
        self.original_data: dict = {}  # task_id -> DataFrame
        self.results: dict = {}  # task_id -> dict
        self.progress_callbacks: dict = {}  # task_id -> callback

    async def start_translation(
        self,
        task_id: str,
        df: pd.DataFrame,
        columns_to_translate: List[str],
        target_languages: List[str],
        progress_callback: Optional[Callable] = None
    ) -> TaskProgress:
        """启动翻译任务"""
        # 初始化进度
        progress = TaskProgress(
            task_id=task_id,
            status="processing",
            total_rows=len(df),
            target_languages=target_languages,
            columns_to_translate=columns_to_translate,
            started_at=datetime.now().isoformat(),
            message="初始化翻译任务..."
        )
        self.tasks[task_id] = progress

        if progress_callback:
            self.progress_callbacks[task_id] = progress_callback

        # 准备数据
        data = df[columns_to_translate].to_dict('records')
        batch_processor = BatchProcessor(data, BATCH_SIZE)
        self.batch_processors[task_id] = batch_processor
        self.original_data[task_id] = df.copy()

        progress.total_batches = len(batch_processor.batches)
        await self._update_progress(task_id, f"开始翻译，共 {progress.total_batches} 个批次")

        # 初始化结果存储
        self.results[task_id] = {
            lang: {col: [] for col in columns_to_translate}
            for lang in target_languages
        }

        # 保存初始状态
        storage.save_task_state(task_id, {
            "progress": progress.__dict__,
            "batch_processor": batch_processor.to_dict()
        })

        # 开始处理批次
        asyncio.create_task(self._process_all_batches(task_id))

        return progress

    async def _process_all_batches(self, task_id: str):
        """处理所有批次"""
        batch_processor = self.batch_processors[task_id]
        progress = self.tasks[task_id]

        try:
            for batch in batch_processor.batches:
                # 更新状态
                batch.status = "translating"
                progress.current_batch = batch.index
                await self._update_progress(
                    task_id,
                    f"翻译批次 {batch.index + 1}/{progress.total_batches}..."
                )

                # 处理单个批次
                success = await self._process_batch(task_id, batch)

                if not success:
                    progress.status = "failed"
                    progress.errors.append(f"批次 {batch.index + 1} 翻译失败")
                    await self._update_progress(task_id, f"翻译失败：批次 {batch.index + 1}")
                    return

                # 更新进度
                batch.status = "completed"
                progress.completed_batches = batch.index + 1
                progress.progress_percent = (progress.completed_batches / progress.total_batches) * 100

                # 保存中间状态
                storage.save_task_state(task_id, {
                    "progress": progress.__dict__,
                    "batch_processor": batch_processor.to_dict()
                })

            # 所有批次完成
            progress.status = "completed"
            progress.completed_at = datetime.now().isoformat()
            await self._update_progress(task_id, "翻译完成，生成结果文件...")

            # 生成结果
            await self._generate_results(task_id)

        except Exception as e:
            progress.status = "failed"
            progress.errors.append(str(e))
            await self._update_progress(task_id, f"翻译失败：{str(e)}")

    async def _process_batch(self, task_id: str, batch: Batch) -> bool:
        """处理单个批次：翻译 + 校验"""
        progress = self.tasks[task_id]
        columns = progress.columns_to_translate
        languages = progress.target_languages

        all_translations = {}

        for lang in languages:
            # 翻译
            batch.status = "translating"
            retry_count = 0
            translated_data = None

            while retry_count < MAX_RETRY:
                try:
                    translated_data = await translator_agent.translate_batch(
                        batch.data, columns, lang
                    )
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= MAX_RETRY:
                        print(f"批次 {batch.index} 翻译失败: {e}")
                        return False
                    await asyncio.sleep(2)  # 等待后重试

            # 校验
            batch.status = "validating"
            await self._update_progress(
                task_id,
                f"校验批次 {batch.index + 1}/{progress.total_batches} ({lang})..."
            )

            validation_result = await validator_agent.validate_batch(
                batch.data, translated_data, columns, lang
            )

            if not validation_result.passed:
                # 如果有修正建议，应用修正
                if validation_result.corrections:
                    for key, correction in validation_result.corrections.items():
                        parts = key.split("_")
                        if len(parts) >= 2:
                            idx = int(parts[0])
                            col = "_".join(parts[1:])
                            if idx < len(translated_data):
                                translated_data[idx][f"{col}_translated"] = correction

                # 记录问题但不失败
                if validation_result.issues:
                    print(f"批次 {batch.index} 校验发现问题: {validation_result.issues}")

            # 保存翻译结果
            all_translations[lang] = translated_data

        # 合并所有语言的翻译结果
        for lang, translations in all_translations.items():
            for i, row in enumerate(translations):
                for col in columns:
                    translated_col = f"{col}_translated"
                    if translated_col in row:
                        self.results[task_id][lang][col].append(row[translated_col])
                    else:
                        self.results[task_id][lang][col].append("")

        return True

    async def _update_progress(self, task_id: str, message: str):
        """更新进度"""
        if task_id in self.tasks:
            self.tasks[task_id].message = message

            # 调用回调
            if task_id in self.progress_callbacks:
                callback = self.progress_callbacks[task_id]
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.tasks[task_id])
                else:
                    callback(self.tasks[task_id])

    async def _generate_results(self, task_id: str):
        """生成结果文件"""
        progress = self.tasks[task_id]
        original_df = self.original_data[task_id]
        results = self.results[task_id]
        columns = progress.columns_to_translate
        languages = progress.target_languages

        # 创建结果 DataFrame
        result_df = original_df.copy()

        for lang in languages:
            lang_code = lang if len(lang) == 2 else {
                "英语": "en", "日语": "ja", "韩语": "ko",
                "法语": "fr", "德语": "de", "西班牙语": "es", "俄语": "ru"
            }.get(lang, lang)

            for col in columns:
                new_col_name = f"{col}_{lang_code}"
                result_df[new_col_name] = results[lang][col]

        # 保存 CSV
        csv_path = storage.save_result_csv(task_id, result_df)

        # 生成预览 HTML
        html = self._generate_preview_html(task_id, result_df, progress)
        html_path = storage.save_result_html(task_id, html)

        await self._update_progress(task_id, f"翻译完成！结果已保存。")

    def _generate_preview_html(
        self,
        task_id: str,
        result_df: pd.DataFrame,
        progress: TaskProgress
    ) -> str:
        """生成预览 HTML"""
        # 表格 HTML
        table_html = result_df.head(50).to_html(
            index=False,
            classes="table table-striped table-hover",
            border=0
        )

        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>翻译结果 - {task_id}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ margin-bottom: 30px; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px 20px; border-radius: 8px; flex: 1; }}
        .stat-card h4 {{ margin: 0; color: #666; font-size: 14px; }}
        .stat-card p {{ margin: 5px 0 0; font-size: 24px; font-weight: bold; color: #333; }}
        .table-container {{ overflow-x: auto; margin-top: 20px; }}
        .table {{ font-size: 14px; min-width: 100%; }}
        .table th {{ background: #f8f9fa; position: sticky; top: 0; }}
        .btn-download {{ margin-top: 20px; }}
        .highlight-col {{ background: #fff3cd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>多语言翻译结果</h1>
            <p class="text-muted">任务 ID: {task_id}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h4>总数据量</h4>
                <p>{progress.total_rows}</p>
            </div>
            <div class="stat-card">
                <h4>处理批次</h4>
                <p>{progress.total_batches}</p>
            </div>
            <div class="stat-card">
                <h4>目标语言</h4>
                <p>{', '.join(progress.target_languages)}</p>
            </div>
            <div class="stat-card">
                <h4>翻译列数</h4>
                <p>{len(progress.columns_to_translate)}</p>
            </div>
        </div>

        <div class="table-container">
            {table_html}
        </div>

        <p class="text-muted mt-3">显示前 50 条数据</p>
    </div>
</body>
</html>
"""

    def get_progress(self, task_id: str) -> Optional[TaskProgress]:
        """获取任务进度"""
        return self.tasks.get(task_id)

    def get_results(self, task_id: str) -> Optional[dict]:
        """获取翻译结果"""
        return self.results.get(task_id)

# 全局实例
orchestrator = Orchestrator()
