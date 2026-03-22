"""存储服务"""
import os
import json
import uuid
import pandas as pd
from datetime import datetime
from typing import Optional
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEMP_DIR, RESULTS_DIR

class StorageService:
    """存储服务"""

    def __init__(self):
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(TEMP_DIR, exist_ok=True)
        os.makedirs(RESULTS_DIR, exist_ok=True)

    def save_upload(self, file_content: bytes, original_filename: str) -> str:
        """保存上传的文件，返回任务ID"""
        task_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task_id}_{timestamp}_{original_filename}"
        filepath = os.path.join(TEMP_DIR, filename)

        with open(filepath, 'wb') as f:
            f.write(file_content)

        return task_id, filepath

    def save_task_state(self, task_id: str, state: dict):
        """保存任务状态"""
        filepath = os.path.join(TEMP_DIR, f"{task_id}_state.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_task_state(self, task_id: str) -> Optional[dict]:
        """加载任务状态"""
        filepath = os.path.join(TEMP_DIR, f"{task_id}_state.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_result_csv(self, task_id: str, df: pd.DataFrame) -> str:
        """保存结果 CSV"""
        filename = f"{task_id}_result.csv"
        filepath = os.path.join(RESULTS_DIR, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        return filepath

    def get_result_csv_path(self, task_id: str) -> Optional[str]:
        """获取结果 CSV 路径"""
        filepath = os.path.join(RESULTS_DIR, f"{task_id}_result.csv")
        return filepath if os.path.exists(filepath) else None

    def save_result_html(self, task_id: str, html_content: str) -> str:
        """保存结果预览 HTML"""
        filepath = os.path.join(RESULTS_DIR, f"{task_id}_preview.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filepath

    def get_result_html_path(self, task_id: str) -> Optional[str]:
        """获取结果预览 HTML 路径"""
        filepath = os.path.join(RESULTS_DIR, f"{task_id}_preview.html")
        return filepath if os.path.exists(filepath) else None

# 全局存储实例
storage = StorageService()
