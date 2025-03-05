from fastapi import UploadFile
import os
from config import settings

def is_valid_file_extension(filename: str) -> bool:
    """
    ファイル拡張子が許可されているかチェック
    """
    ext = filename.split(".")[-1].lower()
    return ext in settings.ALLOWED_EXTENSIONS

def is_valid_file_size(file_size: int) -> bool:
    """
    ファイルサイズが許可範囲内かチェック
    """
    return file_size <= settings.MAX_FILE_SIZE