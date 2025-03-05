from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import List, Dict

from services.data_service import get_company_data
from services.llm_service import generate_sales_text

router = APIRouter()

@router.get("/sales-text-stream")
async def stream_sales_text(request: Request):
    """
    営業文面の生成をストリーミングするエンドポイント
    """
    async def event_generator():
        try:
            # クエリパラメータからリストIDを取得
            list_id = request.query_params.get("list_id")
            
            # 会社データの取得（実際の実装ではDBなどから取得）
            companies = await get_company_data(list_id)
            
            # 各会社について営業文面を生成
            for company in companies:
                # 進捗状況の通知
                progress_data = json.dumps({
                    "status": "processing",
                    "id": company["id"],
                    "message": f"{company.get('company_name', '不明')}の営業文面を生成中..."
                })
                yield f"data: {progress_data}\n\n"
                
                # 営業文面の生成
                sales_text = await generate_sales_text(company)
                
                # 生成結果の送信
                result_data = json.dumps({
                    "id": company["id"],
                    "text": sales_text
                })
                yield f"data: {result_data}\n\n"
                
                # 少し待機（サーバー負荷軽減のため）
                await asyncio.sleep(0.5)
            
            # 全ての処理が完了したことを通知
            yield "data: {\"status\": \"done\"}\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"
            yield "data: {\"status\": \"done\"}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )