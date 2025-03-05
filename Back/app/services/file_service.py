from fastapi import UploadFile, HTTPException
import os
import aiofiles
from config import settings

async def validate_file(file: UploadFile) -> bool:
    """
    アップロードされたファイルを検証する
    """
    # ファイル拡張子の検証
    ext = file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {ext}. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}")
    
    # ファイルサイズの検証（ヘッダーから取得できる場合）
    content_length = file.size if hasattr(file, "size") else None
    if content_length and content_length > settings.MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds the limit of {settings.MAX_FILE_SIZE / (1024 * 1024)}MB")
    
    return True

async def save_file(file: UploadFile, filename: str) -> str:
    """
    アップロードされたファイルを保存する
    """
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # ディレクトリが存在することを確認
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # ファイルを保存
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return file_path