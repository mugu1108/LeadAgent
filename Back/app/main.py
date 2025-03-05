from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from routers import upload, process, stream, export

# アプリケーションの作成
app = FastAPI(
    title="営業リスト処理API",
    description="営業リストを受け取り、構造化するAPIサービス",
    version="0.1.0"
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのオリジン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(process.router, prefix="/api", tags=["process"])
app.include_router(stream.router, prefix="/api", tags=["stream"])
app.include_router(export.router, prefix="/api", tags=["export"])

# アップロードディレクトリの作成
os.makedirs("uploads", exist_ok=True)

# 環境変数の読み込み
load_dotenv()

@app.get("/")
async def root():
    return {"message": "営業リスト処理APIへようこそ"}

@app.get("/api/test-data")
async def test_data():
    """
    テスト用のデータを返すエンドポイント
    """
    return {
        "data": [
            {
                "id": "test-1",
                "company_name": "テスト株式会社",
                "industry": "IT",
                "contact_person": "山田太郎",
                "email": "test@example.com",
                "phone": "03-1234-5678",
                "address": "東京都渋谷区",
                "url": "https://example.com",
                "employee_count": 100,
                "revenue": 500,
                "established_year": 2010,
                "status": "処理中"
            },
            {
                "id": "test-2",
                "company_name": "サンプル商事",
                "industry": "製造業",
                "contact_person": "佐藤次郎",
                "email": "sample@example.com",
                "phone": "03-8765-4321",
                "address": "大阪府大阪市",
                "url": "https://sample.com",
                "employee_count": 50,
                "revenue": 300,
                "established_year": 2005,
                "status": "処理中"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)