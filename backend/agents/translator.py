"""翻译 Agent"""
import aiohttp
import json
from typing import List, Dict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_API_URL, LLM_API_KEY, LLM_MODEL, get_language_name

class TranslatorAgent:
    """翻译 Agent - 负责将文本翻译成目标语言"""

    def __init__(self):
        self.api_url = LLM_API_URL
        self.api_key = LLM_API_KEY
        self.model = LLM_MODEL

    async def translate_batch(
        self,
        batch_data: List[Dict],
        columns_to_translate: List[str],
        target_language: str
    ) -> List[Dict]:
        """翻译一个批次的数据

        Args:
            batch_data: 批次数据列表
            columns_to_translate: 需要翻译的列名列表
            target_language: 目标语言

        Returns:
            翻译后的数据列表
        """
        # 获取语言名称
        lang_name = get_language_name(target_language)

        # 构建待翻译数据
        texts_to_translate = []
        for row in batch_data:
            row_texts = {}
            for col in columns_to_translate:
                if col in row and row[col]:
                    row_texts[col] = str(row[col])
            texts_to_translate.append(row_texts)

        # 构建 prompt
        prompt = self._build_translation_prompt(texts_to_translate, lang_name)

        # 调用 LLM
        response = await self._call_llm(prompt)

        # 解析结果
        translated_data = self._parse_translation_response(response, batch_data, columns_to_translate)

        return translated_data

    def _build_translation_prompt(self, texts_to_translate: List[Dict], target_language: str) -> str:
        """构建翻译 prompt"""
        return f"""你是一个专业翻译助手。请将以下 JSON 数据中的中文内容翻译成{target_language}。

要求：
1. 保持专业术语的准确性
2. 数字、日期、单位格式保持不变（如 "2024-01-01", "100kg", "¥99" 等不要翻译）
3. 保持 JSON 格式一致，只翻译文本内容
4. 如果原文包含品牌名、专有名词，保持原文不变

待翻译数据（JSON 数组格式）：
```json
{json.dumps(texts_to_translate, ensure_ascii=False, indent=2)}
```

请直接返回翻译后的 JSON 数组，格式与输入完全一致。不要添加任何解释或备注。"""

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的多语言翻译助手，擅长准确、流畅地将中文翻译成各种语言。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 降低温度提高翻译稳定性
            "max_tokens": 4096
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"LLM API 调用失败: {response.status} - {error_text}")

    def _parse_translation_response(
        self,
        response: str,
        original_data: List[Dict],
        columns_to_translate: List[str]
    ) -> List[Dict]:
        """解析翻译响应"""
        try:
            # 尝试提取 JSON
            json_match = response
            if "```json" in response:
                json_match = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_match = response.split("```")[1].split("```")[0]

            translated_texts = json.loads(json_match.strip())

            # 合并翻译结果到原始数据
            result = []
            for i, row in enumerate(original_data):
                new_row = dict(row)
                if i < len(translated_texts):
                    for col in columns_to_translate:
                        if col in translated_texts[i]:
                            new_row[f"{col}_translated"] = translated_texts[i][col]
                result.append(new_row)

            return result

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # 解析失败，返回原始数据并标记
            print(f"翻译响应解析失败: {e}")
            return [
                {**row, **{f"{col}_translated": row.get(col, "") for col in columns_to_translate}}
                for row in original_data
            ]

# 全局实例
translator_agent = TranslatorAgent()
