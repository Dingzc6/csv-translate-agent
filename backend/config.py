"""配置文件"""
import os

# LLM 配置
LLM_API_URL = os.environ.get("LLM_API_URL", "https://ai.t8star.cn/v1/chat/completions")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "sk-AvlxHNfcuoy31ylKB3Om14lEEzhWLWia9LDDUJyPeU5fsaie")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-5.4")

# Batch 配置
BATCH_SIZE = 20  # 每批处理条数
MAX_RETRY = 3    # 最大重试次数

# 存储路径
TEMP_DIR = "temp"
RESULTS_DIR = "results"

# 语言映射 - 支持多种输入格式
LANGUAGE_TO_ENGLISH = {
    # 语言代码
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
    "ar": "Arabic",
    "th": "Thai",
    "vi": "Vietnamese",
    # 中文名称
    "英语": "English",
    "日语": "Japanese",
    "韩语": "Korean",
    "法语": "French",
    "德语": "German",
    "西班牙语": "Spanish",
    "俄语": "Russian",
    "葡萄牙语": "Portuguese",
    "意大利语": "Italian",
    "阿拉伯语": "Arabic",
    "泰语": "Thai",
    "越南语": "Vietnamese",
    # 英文名称
    "english": "English",
    "japanese": "Japanese",
    "korean": "Korean",
    "french": "French",
    "german": "German",
    "spanish": "Spanish",
    "russian": "Russian",
    "portuguese": "Portuguese",
    "italian": "Italian",
    "arabic": "Arabic",
    "thai": "Thai",
    "vietnamese": "Vietnamese",
    # 更多语言
    "荷兰语": "Dutch",
    "dutch": "Dutch",
    "nl": "Dutch",
    "瑞典语": "Swedish",
    "swedish": "Swedish",
    "sv": "Swedish",
    "印地语": "Hindi",
    "hindi": "Hindi",
    "hi": "Hindi",
    "土耳其语": "Turkish",
    "turkish": "Turkish",
    "tr": "Turkish",
    "波兰语": "Polish",
    "polish": "Polish",
    "pl": "Polish",
    "印尼语": "Indonesian",
    "indonesian": "Indonesian",
    "id": "Indonesian",
    "马来语": "Malay",
    "malay": "Malay",
    "ms": "Malay",
}

def get_language_name(code_or_name):
    """获取语言的英文名称，支持中文、英文、语言代码输入"""
    code_or_name_lower = code_or_name.lower() if isinstance(code_or_name, str) else code_or_name

    # 先尝试精确匹配
    if code_or_name in LANGUAGE_TO_ENGLISH:
        return LANGUAGE_TO_ENGLISH[code_or_name]

    # 再尝试小写匹配
    if code_or_name_lower in LANGUAGE_TO_ENGLISH:
        return LANGUAGE_TO_ENGLISH[code_or_name_lower]

    # 原样返回（让 LLM 处理自定义语言）
    return code_or_name
