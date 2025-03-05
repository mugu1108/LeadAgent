import re
import unicodedata
from typing import Dict, Any

def normalize_text(text: str) -> str:
    """
    テキストを正規化する
    """
    # 全角を半角に変換
    text = unicodedata.normalize('NFKC', text)
    # 余分な空白を削除
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_error_response(error_code: str, message: str) -> Dict[str, Any]:
    """
    エラーレスポンスを整形する
    """
    return {
        "success": False,
        "error": message,
        "error_code": error_code
    }