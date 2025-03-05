import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # アプリケーション設定
    APP_NAME: str = "営業リスト処理API"
    DEBUG: bool = True
    
    # ファイルアップロード設定
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["xlsx", "xls", "csv"]
    
    # データ処理設定
    REQUIRED_COLUMNS: list = ["会社名"]  # 必須カラム
    
    class Config:
        env_file = ".env"

settings = Settings()