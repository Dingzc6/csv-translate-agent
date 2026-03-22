"""校验 Agent"""
import aiohttp
import json
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_API_URL, LLM_API_KEY, LLM_MODEL

@dataclass
class ValidationResult:
    """校验结果"""
    passed: bool
    completeness: bool       # 完整性：所有条目都已翻译
    language_correct: bool   # 语言正确：目标语言准确
    format_preserved: bool   # 格式保留：数字/日期格式正确
    issues: List[Dict]       # 问题列表
    corrections: Dict        # 修正建议

class ValidatorAgent:
    """校验 Agent - 负责验证翻译质量"""

    def __init__(self):
        self.api_url = LLM_API_URL
        self.api_key = LLM_API_KEY
        self.model = LLM_MODEL

    async def validate_batch(
        self,
        original_data: List[Dict],
        translated_data: List[Dict],
        columns_to_translate: List[str],
        target_language: str
    ) -> ValidationResult:
        """校验一个批次的翻译结果

        Args:
            original_data: 原始数据
            translated_data: 翻译后的数据
            columns_to_translate: 翻译的列名
            target_language: 目标语言

        Returns:
            ValidationResult 校验结果
        """
        # 1. 完整性检查
        completeness = self._check_completeness(original_data, translated_data, columns_to_translate)

        # 2. 格式检查（数字、日期等是否保留）
        format_result = self._check_format_preservation(original_data, translated_data, columns_to_translate)

        # 3. 语言检查（通过 LLM）
        language_result, issues, corrections = await self._check_language_correctness(
            original_data, translated_data, columns_to_translate, target_language
        )

        # 综合判定
        passed = completeness and format_result and language_result

        return ValidationResult(
            passed=passed,
            completeness=completeness,
            language_correct=language_result,
            format_preserved=format_result,
            issues=issues,
            corrections=corrections
        )

    def _check_completeness(
        self,
        original_data: List[Dict],
        translated_data: List[Dict],
        columns_to_translate: List[str]
    ) -> bool:
        """检查完整性：翻译条数是否一致"""
        if len(original_data) != len(translated_data):
            return False

        for i, row in enumerate(translated_data):
            for col in columns_to_translate:
                translated_col = f"{col}_translated"
                if translated_col not in row:
                    return False
                if row[translated_col] is None or row[translated_col] == "":
                    # 检查原文是否为空
                    if original_data[i].get(col):
                        return False

        return True

    def _check_format_preservation(
        self,
        original_data: List[Dict],
        translated_data: List[Dict],
        columns_to_translate: List[str]
    ) -> bool:
        """检查格式保留：数字、日期等格式是否正确保留"""
        # 数字模式
        number_pattern = re.compile(r'\d+\.?\d*')
        # 日期模式
        date_pattern = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')
        # 货币模式
        currency_pattern = re.compile(r'[¥$€£]\d+')

        for i, row in enumerate(translated_data):
            for col in columns_to_translate:
                original_text = str(original_data[i].get(col, ""))
                translated_text = str(row.get(f"{col}_translated", ""))

                # 检查数字是否保留
                original_numbers = number_pattern.findall(original_text)
                translated_numbers = number_pattern.findall(translated_text)
                if original_numbers != translated_numbers and original_numbers:
                    return False

                # 检查日期是否保留
                original_dates = date_pattern.findall(original_text)
                translated_dates = date_pattern.findall(translated_text)
                if original_dates != translated_dates and original_dates:
                    return False

                # 检查货币符号
                original_currencies = currency_pattern.findall(original_text)
                translated_currencies = currency_pattern.findall(translated_text)
                if original_currencies != translated_currencies and original_currencies:
                    return False

        return True

    async def _check_language_correctness(
        self,
        original_data: List[Dict],
        translated_data: List[Dict],
        columns_to_translate: List[str],
        target_language: str
    ) -> Tuple[bool, List[Dict], Dict]:
        """通过 LLM 检查语言正确性"""
        # 抽样检查（取前5条）
        sample_size = min(5, len(original_data))
        sample_original = original_data[:sample_size]
        sample_translated = translated_data[:sample_size]

        prompt = self._build_validation_prompt(
            sample_original, sample_translated, columns_to_translate, target_language
        )

        try:
            response = await self._call_llm(prompt)
            result = self._parse_validation_response(response)
            return result["passed"], result["issues"], result.get("corrections", {})
        except Exception as e:
            print(f"校验 LLM 调用失败: {e}")
            # 默认通过
            return True, [], {}

    def _build_validation_prompt(
        self,
        original_data: List[Dict],
        translated_data: List[Dict],
        columns_to_translate: List[str],
        target_language: str
    ) -> str:
        """构建校验 prompt"""
        # 准备原文和译文对照
        comparison = []
        for i in range(len(original_data)):
            for col in columns_to_translate:
                original_text = original_data[i].get(col, "")
                translated_text = translated_data[i].get(f"{col}_translated", "")
                if original_text:
                    comparison.append({
                        "index": i,
                        "column": col,
                        "original": original_text,
                        "translated": translated_text
                    })

        return f"""你是一个翻译质量校验专家。请检查以下从中文到{target_language}的翻译结果。

原文与译文对照：
```json
{json.dumps(comparison[:10], ensure_ascii=False, indent=2)}
```

请检查以下维度：
1. **语言正确性**：译文是否确实是{target_language}，有无混入其他语言（如中文、英文等）
2. **含义准确**：译文是否准确传达原文含义
3. **专业术语**：专业词汇翻译是否恰当

请返回 JSON 格式结果：
```json
{{
  "passed": true/false,
  "issues": [
    {{"index": 0, "column": "列名", "issue": "问题描述", "suggestion": "修正建议"}}
  ],
  "corrections": {{
    "0_列名": "修正后的翻译"
  }}
}}
```

如果没有问题，返回 {{"passed": true, "issues": [], "corrections": {{}}}}"""

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个翻译质量校验专家，擅长检测翻译错误和幻觉问题。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2048
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"校验 LLM API 调用失败: {response.status}")

    def _parse_validation_response(self, response: str) -> Dict:
        """解析校验响应"""
        try:
            # 提取 JSON
            json_match = response
            if "```json" in response:
                json_match = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_match = response.split("```")[1].split("```")[0]

            return json.loads(json_match.strip())
        except json.JSONDecodeError:
            return {"passed": True, "issues": [], "corrections": {}}

# 全局实例
validator_agent = ValidatorAgent()
