"""Batch 分片处理器"""
import json
from typing import List, Generator, Any
from dataclasses import dataclass

@dataclass
class Batch:
    """批次数据类"""
    index: int          # 批次索引（从0开始）
    start_row: int      # 起始行号（从0开始）
    end_row: int        # 结束行号
    data: List[dict]    # 批次数据
    status: str = "pending"  # pending, translating, validating, completed, failed
    retry_count: int = 0
    result: List[dict] = None

class BatchProcessor:
    """Batch 处理器"""

    def __init__(self, data: List[dict], batch_size: int = 20):
        self.data = data
        self.batch_size = batch_size
        self.batches: List[Batch] = []
        self._create_batches()

    def _create_batches(self):
        """创建批次"""
        total = len(self.data)
        for i in range(0, total, self.batch_size):
            end = min(i + self.batch_size, total)
            batch = Batch(
                index=len(self.batches),
                start_row=i,
                end_row=end,
                data=self.data[i:end]
            )
            self.batches.append(batch)

    def get_batch(self, index: int) -> Batch:
        """获取指定批次"""
        if 0 <= index < len(self.batches):
            return self.batches[index]
        return None

    def get_pending_batch(self) -> Batch:
        """获取下一个待处理的批次"""
        for batch in self.batches:
            if batch.status == "pending":
                return batch
        return None

    def update_batch_status(self, index: int, status: str, result: List[dict] = None):
        """更新批次状态"""
        if 0 <= index < len(self.batches):
            self.batches[index].status = status
            if result:
                self.batches[index].result = result

    def increment_retry(self, index: int) -> int:
        """增加重试次数，返回当前重试次数"""
        if 0 <= index < len(self.batches):
            self.batches[index].retry_count += 1
            return self.batches[index].retry_count
        return 0

    def get_progress(self) -> dict:
        """获取进度信息"""
        total = len(self.batches)
        completed = sum(1 for b in self.batches if b.status == "completed")
        failed = sum(1 for b in self.batches if b.status == "failed")
        in_progress = sum(1 for b in self.batches if b.status in ["translating", "validating"])

        return {
            "total_batches": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "progress_percent": int((completed / total) * 100) if total > 0 else 0,
            "current_batch": next(
                (b.index for b in self.batches if b.status in ["translating", "validating"]),
                None
            )
        }

    def get_all_results(self) -> List[dict]:
        """获取所有批次的结果"""
        results = []
        for batch in self.batches:
            if batch.result:
                results.extend(batch.result)
        return results

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "batch_size": self.batch_size,
            "total_data": len(self.data),
            "batches": [
                {
                    "index": b.index,
                    "start_row": b.start_row,
                    "end_row": b.end_row,
                    "status": b.status,
                    "retry_count": b.retry_count,
                    "has_result": b.result is not None
                }
                for b in self.batches
            ]
        }
