"""CSV 解析服务"""
import pandas as pd
import re
from typing import List, Tuple

def detect_chinese_columns(df: pd.DataFrame) -> List[str]:
    """检测包含中文的列"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    chinese_columns = []

    for col in df.columns:
        # 检查列名是否包含中文
        if chinese_pattern.search(str(col)):
            chinese_columns.append(col)
            continue

        # 检查列内容是否包含中文
        sample = df[col].dropna().head(50).astype(str)
        chinese_count = sum(1 for val in sample if chinese_pattern.search(val))
        if chinese_count > len(sample) * 0.3:  # 超过30%包含中文
            chinese_columns.append(col)

    return chinese_columns

def parse_csv(file_path: str) -> Tuple[pd.DataFrame, dict]:
    """解析 CSV 文件，返回 DataFrame 和统计信息"""
    # 尝试不同编码
    for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("无法解析 CSV 文件编码")

    # 检测中文列
    chinese_columns = detect_chinese_columns(df)

    # 统计信息
    stats = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "chinese_columns": chinese_columns,
        "columns": list(df.columns),
        "preview": df.head(5).to_dict('records')
    }

    return df, stats

def create_result_csv(
    original_df: pd.DataFrame,
    translations: dict,
    target_languages: List[str]
) -> pd.DataFrame:
    """创建结果 CSV"""
    result_df = original_df.copy()

    # 获取需要翻译的列
    columns_to_translate = [col for col in translations.keys()]

    for col in columns_to_translate:
        col_translations = translations[col]
        for lang in target_languages:
            lang_code = lang if len(lang) == 2 else {
                "英语": "en", "日语": "ja", "韩语": "ko",
                "法语": "fr", "德语": "de", "西班牙语": "es", "俄语": "ru"
            }.get(lang, lang)

            new_col_name = f"{col}_{lang_code}"
            result_df[new_col_name] = col_translations.get(lang, [])

    return result_df
